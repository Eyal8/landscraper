"""Verify the actual App Store-signed IPA before uploading that exact file."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile


def run(*args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def require(condition, message):
    if not condition:
        raise SystemExit("Release verification failed: " + message)


def verify_profile(entitlements, profile, team):
    app_id = team + ".com.beno74.landscraper"
    require(entitlements.get("application-identifier") == app_id, "signed application ID")
    require(entitlements.get("com.apple.developer.team-identifier") == team, "signing team")
    require(entitlements.get("com.apple.developer.game-center") is True, "signed Game Center entitlement")
    require(entitlements.get("get-task-allow") is False, "development-signed app cannot be uploaded")
    require(entitlements.get("beta-reports-active") is True, "TestFlight entitlement")
    allowed = profile["Entitlements"]
    require(allowed.get("application-identifier") == app_id, "profile application ID")
    require(allowed.get("com.apple.developer.game-center") is True, "profile Game Center entitlement")
    require(allowed.get("get-task-allow") is False, "development provisioning profile")
    require(not profile.get("ProvisionedDevices") and not profile.get("ProvisionsAllDevices"), "App Store profile required")
    require(profile["ExpirationDate"] > datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None), "expired profile")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir", required=True, type=Path)
    parser.add_argument("--build", required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(run("git", "rev-parse", "HEAD").decode().strip() == args.source_sha, "checkout does not match source SHA")
    require(not run("git", "diff", "--name-only").strip(), "tracked source changed during build")
    ipas = list(args.export_dir.glob("*.ipa"))
    require(len(ipas) == 1, "expected exactly one exported IPA")
    ipa = ipas[0].resolve()
    with tempfile.TemporaryDirectory() as temp:
        run("ditto", "-x", "-k", str(ipa), temp)
        apps = list((Path(temp) / "Payload").glob("*.app"))
        require(len(apps) == 1, "expected exactly one main app")
        app = apps[0]
        info = plistlib.loads((app / "Info.plist").read_bytes())
        require(info.get("CFBundleIdentifier") == "com.beno74.landscraper", "bundle ID")
        require(info.get("CFBundleShortVersionString") == "1.0", "marketing version")
        require(info.get("CFBundleVersion") == args.build, "build number")
        run("codesign", "--verify", "--deep", "--strict", str(app))
        entitlements = plistlib.loads(run("codesign", "-d", "--entitlements", ":-", str(app)))
        profile = plistlib.loads(run("security", "cms", "-D", "-i", str(app / "embedded.mobileprovision")))
        verify_profile(entitlements, profile, args.team)
        require(b"GameKit.framework/GameKit" in run("otool", "-L", str(app / info["CFBundleExecutable"])), "GameKit not linked")
        html = (app / "public/index.html").read_bytes()
        require(html == Path("www/index.html").read_bytes(), "packaged web content differs from verified source build")
        require(0 <= html.find(b'<script src="capacitor.js"></script>') < html.find(b"window.Board ="), "Capacitor startup order")
        for kind in ("daily", "rush"):
            require(("com.beno74.landscraper." + kind).encode() in html, "missing " + kind + " leaderboard ID")
        report = {
            "source_sha": args.source_sha,
            "branch": os.environ.get("GITHUB_REF_NAME"),
            "bundle_id": info["CFBundleIdentifier"],
            "version": info["CFBundleShortVersionString"],
            "build": info["CFBundleVersion"],
            "team": args.team,
            "game_center": True,
            "get_task_allow": False,
            "beta_reports_active": True,
            "profile_uuid": profile["UUID"],
            "ipa_path": str(ipa),
            "ipa_sha256": hashlib.sha256(ipa.read_bytes()).hexdigest(),
        }
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
