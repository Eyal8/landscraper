import Capacitor
import DeclaredAgeRange
import GoogleMobileAds
import GameKit
import UIKit

// The app's bridge controller: registers the local Game Center plugin.
class MainViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        bridge?.registerPluginInstance(GamesPlugin())
        bridge?.registerPluginInstance(AnalyticsConsentPlugin())
        bridge?.registerPluginInstance(RegionalAgePlugin())
        // A screenshot does not pause the app by itself: tell the game, so it pauses
        NotificationCenter.default.addObserver(forName: UIApplication.userDidTakeScreenshotNotification, object: nil, queue: .main) { [weak self] _ in
            self?.bridge?.webView?.evaluateJavaScript("window.__shot && window.__shot()", completionHandler: nil)
        }
    }
    // Steering often starts near the screen edges: let the game have the first swipe there (the home bar waits for a second one).
    override open var preferredScreenEdgesDeferringSystemGestures: UIRectEdge { .all }
}

// Game Center: sign-in, submit a score, open a leaderboard. JS name: "Games".
@objc(GamesPlugin)
public class GamesPlugin: CAPPlugin, CAPBridgedPlugin, GKGameCenterControllerDelegate {
    public let identifier = "GamesPlugin"
    public let jsName = "Games"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "signIn", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "submitScore", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "showLeaderboard", returnType: CAPPluginReturnPromise)
    ]
    private var started = false

    @objc func signIn(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            if GKLocalPlayer.local.isAuthenticated { call.resolve(["authenticated": true]); return }
            if self.started { call.resolve(["authenticated": false]); return }
            self.started = true
            var answered = false
            GKLocalPlayer.local.authenticateHandler = { [weak self] vc, _ in
                if let vc = vc {
                    self?.bridge?.viewController?.present(vc, animated: true)
                    return
                }
                if !answered { answered = true; call.resolve(["authenticated": GKLocalPlayer.local.isAuthenticated]) }
            }
        }
    }

    @objc func submitScore(_ call: CAPPluginCall) {
        guard let id = call.getString("id"), let score = call.getInt("score") else { call.reject("id and score are required"); return }
        guard GKLocalPlayer.local.isAuthenticated else { call.reject("not signed in"); return }
        GKLeaderboard.submitScore(score, context: 0, player: GKLocalPlayer.local, leaderboardIDs: [id]) { error in
            if let error = error { call.reject(error.localizedDescription) } else { call.resolve() }
        }
    }

    @objc func showLeaderboard(_ call: CAPPluginCall) {
        let id = call.getString("id") ?? ""
        DispatchQueue.main.async {
            let vc = GKGameCenterViewController(leaderboardID: id, playerScope: .global, timeScope: .allTime)
            vc.gameCenterDelegate = self
            self.bridge?.viewController?.present(vc, animated: true)
            call.resolve()
        }
    }

    public func gameCenterViewControllerDidFinish(_ gameCenterViewController: GKGameCenterViewController) {
        gameCenterViewController.dismiss(animated: true)
    }
}

// UMP uses the app's standard preferences on iOS. Missing signals remain empty.
@objc(AnalyticsConsentPlugin)
public class AnalyticsConsentPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "AnalyticsConsentPlugin"
    public let jsName = "AnalyticsConsent"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "getConsentModes", returnType: CAPPluginReturnPromise)
    ]

    @objc func getConsentModes(_ call: CAPPluginCall) {
        call.resolve(["values": UserDefaults.standard.string(forKey: "UMP_consentModeValues") ?? ""])
    }
}
// Apple describes upperBound as an age gate exceeding the person's age.
// Accept both threshold bounds (18) and narrower regional bounds (17).
private func regionalAgeClassification(lower: Int?, upper: Int?) -> JSObject {
    if let lower, lower >= 18 {
        return ["status": "resolved", "minor": false, "childDirected": false]
    }
    if let upper, upper <= 18 {
        return ["status": "resolved", "minor": true, "childDirected": lower == nil || (lower ?? 0) < 13]
    }
    return ["status": "unresolved"]
}

// No age data is persisted or logged. Sharing is requested only after Apple's regional gate.
@objc(RegionalAgePlugin)
public class RegionalAgePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "RegionalAgePlugin"
    public let jsName = "RegionalAge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "getRequirements", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "requestRequiredAgeRange", returnType: CAPPluginReturnPromise)
    ]
    private var requesting = false

    @objc func getRequirements(_ call: CAPPluginCall) {
        Task { @MainActor in call.resolve(await self.requirements()) }
    }

    // This check never calls requestAgeRange and cannot present its sharing sheet.
    @MainActor private func requirements() async -> JSObject {
        guard #available(iOS 26.2, *) else { return ["status": "unsupported"] }
        do {
            let required: Bool
            if #available(iOS 26.4, *) {
                let features = try await AgeRangeService.shared.requiredRegulatoryFeatures
                required = features.contains(.declaredAgeRangeRequired)
            } else {
                required = try await AgeRangeService.shared.isEligibleForAgeFeatures
            }
            return ["status": required ? "required" : "notRequired"]
        } catch AgeRangeService.Error.notAvailable {
            return ["status": "unavailable"]
        } catch {
            return ["status": "error"]
        }
    }

    @objc func requestRequiredAgeRange(_ call: CAPPluginCall) {
        Task { @MainActor in
            guard !self.requesting else { call.resolve(["status": "unresolved"]); return }
            self.requesting = true
            defer { self.requesting = false }
            let current = await self.requirements()
            guard current["status"] as? String == "required" else { call.resolve(current); return }
            guard #available(iOS 26.2, *), let controller = self.bridge?.viewController,
                  controller.viewIfLoaded?.window != nil,
                  controller.presentedViewController == nil else {
                call.resolve(["status": "unresolved"])
                return
            }
            do {
                let response = try await AgeRangeService.shared.requestAgeRange(ageGates: 13, 16, 18, in: controller)
                switch response {
                case .declinedSharing:
                    call.resolve(["status": "declined"])
                case .sharing(let range):
                    let result = regionalAgeClassification(lower: range.lowerBound, upper: range.upperBound)
                    if result["status"] as? String == "resolved" {
                        // Current GMA distinguishes teen privacy treatment from child treatment.
                        // Configure it before JavaScript is allowed to initialize/load ads.
                        let config = MobileAds.shared.requestConfiguration
                        if result["minor"] as? Bool == true {
                            config.ageRestrictedTreatment = result["childDirected"] as? Bool == true ? .child : .teen
                        } else {
                            config.ageRestrictedTreatment = .unspecified
                        }
                    }
                    call.resolve(result)
                @unknown default:
                    call.resolve(["status": "unresolved"])
                }
            } catch AgeRangeService.Error.notAvailable {
                call.resolve(["status": "unavailable"])
            } catch {
                call.resolve(["status": "error"])
            }
        }
    }
}
