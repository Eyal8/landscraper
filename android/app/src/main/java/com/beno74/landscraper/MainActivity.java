package com.beno74.landscraper;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
import com.google.android.gms.games.PlayGamesSdk;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(GamesPlugin.class);
        super.onCreate(savedInstanceState);
        PlayGamesSdk.initialize(this);
    }
}
