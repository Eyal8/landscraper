package com.beno74.landscraper;

import android.graphics.Rect;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import com.getcapacitor.BridgeActivity;
import com.google.android.gms.games.PlayGamesSdk;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(GamesPlugin.class);
        super.onCreate(savedInstanceState);
        PlayGamesSdk.initialize(this);
        // Gesture navigation: a swipe in from the left or right edge means Back. Keep the lower part of both edges for
        // steering (Android allows up to 200dp per edge), where the touch pad is usually opened.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            final View root = getWindow().getDecorView();
            root.addOnLayoutChangeListener((v, l, t, r, b, ol, ot, or, ob) -> {
                float dp = getResources().getDisplayMetrics().density;
                int w = r - l, h = b - t, band = (int) (200 * dp), edge = (int) (40 * dp);
                List<Rect> rects = new ArrayList<>();
                rects.add(new Rect(0, h - band, edge, h));
                rects.add(new Rect(w - edge, h - band, w, h));
                v.setSystemGestureExclusionRects(rects);
            });
        }
    }
}
