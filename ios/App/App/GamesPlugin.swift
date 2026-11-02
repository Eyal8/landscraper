import Capacitor
import GameKit
import UIKit
import OSLog

// The app's bridge controller: registers the local Game Center plugin.
class MainViewController: CAPBridgeViewController {
    private let games = GamesPlugin()

    override open func capacitorDidLoad() {
        bridge?.registerPluginInstance(games)
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        games.startAuthentication()
    }
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
    private var authenticating = false
    private var pendingCalls: [CAPPluginCall] = []
    private var authenticationController: UIViewController?
    private var authenticationError: NSError?
    private let log = Logger(subsystem: "com.beno74.landscraper", category: "GameCenter")
    private let leaderboardIDs = ["com.beno74.landscraper.daily", "com.beno74.landscraper.rush"]

    public override func load() {
        log.notice("Games bridge registered")
        NotificationCenter.default.addObserver(self, selector: #selector(becameActive), name: UIApplication.didBecomeActiveNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(authenticationChanged), name: .GKPlayerAuthenticationDidChangeNotificationName, object: nil)
    }

    deinit { NotificationCenter.default.removeObserver(self) }

    // Called after the app's controller appears, without a timing guess.
    func startAuthentication() {
        dispatchPrecondition(condition: .onQueue(.main))
        guard !started else { presentAuthenticationIfReady(); return }
        started = true
        authenticating = true
        log.notice("Installing GameKit authentication handler")
        GKLocalPlayer.local.authenticateHandler = { [weak self] controller, error in
            DispatchQueue.main.async {
                guard let self = self else { return }
                self.authenticationError = error as NSError?
                self.log.notice("Authentication callback: authenticated=\(GKLocalPlayer.local.isAuthenticated), requiresUI=\(controller != nil)")
                if let error = self.authenticationError { self.record(error, operation: "authentication") }
                if let controller = controller {
                    self.authenticating = true
                    self.authenticationController = controller
                    self.presentAuthenticationIfReady()
                } else {
                    self.authenticating = false
                    self.authenticationController = nil
                    let calls = self.pendingCalls
                    self.pendingCalls.removeAll()
                    calls.forEach { self.answer($0) }
                    self.authenticationChanged()
                }
            }
        }
    }

    @objc private func becameActive() {
        // GameKit rechecks the account on foregrounding; retain its handler.
        presentAuthenticationIfReady()
        authenticationChanged()
    }

    @objc private func authenticationChanged() {
        DispatchQueue.main.async {
            self.log.notice("Authentication state: authenticated=\(GKLocalPlayer.local.isAuthenticated)")
            self.notifyListeners("authenticationChanged", data: ["authenticated": GKLocalPlayer.local.isAuthenticated], retainUntilConsumed: true)
        }
    }

    private func presentAuthenticationIfReady() {
        guard let controller = authenticationController,
              let presenter = bridge?.viewController,
              presenter.viewIfLoaded?.window != nil,
              UIApplication.shared.applicationState == .active,
              presenter.presentedViewController == nil else { return }
        presenter.present(controller, animated: true) {
            self.log.notice("GameKit authentication UI presented")
        }
    }

    private func record(_ error: NSError, operation: String) {
        // Domain/code only: no player identifiers, account details or error payloads.
        log.error("\(operation, privacy: .public) failed: domain=\(error.domain, privacy: .public), code=\(error.code)")
    }

    private func answer(_ call: CAPPluginCall) {
        if GKLocalPlayer.local.isAuthenticated {
            call.resolve(["authenticated": true])
        } else if let error = authenticationError {
            call.reject("Game Center authentication failed", "\(error.domain):\(error.code)")
        } else {
            call.resolve(["authenticated": false])
        }
    }

    @objc func signIn(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            self.startAuthentication()
            if self.authenticating && !GKLocalPlayer.local.isAuthenticated {
                self.pendingCalls.append(call)
            } else { self.answer(call) }
        }
    }

    @objc func submitScore(_ call: CAPPluginCall) {
        guard let id = call.getString("id"), let score = call.getInt("score") else { call.reject("id and score are required"); return }
        guard leaderboardIDs.contains(id) else { call.reject("Unknown leaderboard", "INVALID_LEADERBOARD"); return }
        guard GKLocalPlayer.local.isAuthenticated else { call.reject("not signed in"); return }
        GKLeaderboard.submitScore(score, context: 0, player: GKLocalPlayer.local, leaderboardIDs: [id]) { error in
            if let error = error as NSError? {
                self.record(error, operation: "submit")
                call.reject("Game Center score submission failed", "\(error.domain):\(error.code)")
            } else { self.log.notice("Score submission completed"); call.resolve() }
        }
    }

    @objc func showLeaderboard(_ call: CAPPluginCall) {
        let id = call.getString("id") ?? ""
        DispatchQueue.main.async {
            guard self.leaderboardIDs.contains(id) else { call.reject("Unknown leaderboard", "INVALID_LEADERBOARD"); return }
            guard GKLocalPlayer.local.isAuthenticated else { call.reject("Game Center is not signed in", "NOT_AUTHENTICATED"); return }
            guard let presenter = self.bridge?.viewController,
                  presenter.viewIfLoaded?.window != nil,
                  UIApplication.shared.applicationState == .active,
                  presenter.presentedViewController == nil else {
                self.log.notice("Leaderboard presentation unavailable")
                call.reject("Game Center presentation is unavailable", "PRESENTATION_UNAVAILABLE")
                return
            }
            let vc = GKGameCenterViewController(leaderboardID: id, playerScope: .global, timeScope: .allTime)
            vc.gameCenterDelegate = self
            presenter.present(vc, animated: true) {
                self.log.notice("Leaderboard UI presented")
                call.resolve()
            }
        }
    }

    public func gameCenterViewControllerDidFinish(_ gameCenterViewController: GKGameCenterViewController) {
        gameCenterViewController.dismiss(animated: true)
    }
}
