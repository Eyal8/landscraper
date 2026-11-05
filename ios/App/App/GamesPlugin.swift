import Capacitor
import GameKit
import UIKit

// The app's bridge controller: registers the local Game Center plugin.
class MainViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        bridge?.registerPluginInstance(GamesPlugin())
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
