package com.beno74.landscraper;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.android.gms.games.GamesSignInClient;
import com.google.android.gms.games.PlayGames;

// Google Play Games: sign-in, submit a score, open a leaderboard. JS name: "Games".
@CapacitorPlugin(name = "Games")
public class GamesPlugin extends Plugin {

    @PluginMethod
    public void signIn(PluginCall call) {
        GamesSignInClient client = PlayGames.getGamesSignInClient(getActivity());
        client.isAuthenticated().addOnCompleteListener(t -> {
            boolean ok = t.isSuccessful() && t.getResult().isAuthenticated();
            if (ok || !call.getBoolean("interactive", false)) { resolve(call, ok); return; }
            client.signIn().addOnCompleteListener(t2 -> resolve(call, t2.isSuccessful() && t2.getResult().isAuthenticated()));
        });
    }

    @PluginMethod
    public void submitScore(PluginCall call) {
        String id = call.getString("id");
        Object raw = call.getData().opt("score"); // small numbers arrive as Integer, large as Long
        if (id == null || !(raw instanceof Number)) { call.reject("id and score are required"); return; }
        long score = ((Number) raw).longValue();
        try {
            PlayGames.getLeaderboardsClient(getActivity()).submitScore(id, score);
            call.resolve();
        } catch (Exception e) { call.reject(e.getMessage()); }
    }

    @PluginMethod
    public void showLeaderboard(PluginCall call) {
        String id = call.getString("id");
        PlayGames.getLeaderboardsClient(getActivity()).getLeaderboardIntent(id)
            .addOnSuccessListener(intent -> { getActivity().startActivityForResult(intent, 9004); call.resolve(); })
            .addOnFailureListener(e -> call.reject(e.getMessage()));
    }

    private void resolve(PluginCall call, boolean ok) {
        JSObject r = new JSObject();
        r.put("authenticated", ok);
        call.resolve(r);
    }
}
