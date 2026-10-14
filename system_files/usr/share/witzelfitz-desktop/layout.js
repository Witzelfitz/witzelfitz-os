// Only add our hub: existing applets, activities and launcher entries remain usable.
var active = desktops();
var installed = 0;
for (var i = 0; i < active.length; ++i) {
    var desktop = active[i];
    desktop.wallpaperPlugin = "io.github.witzelfitz.anime";
    // Keep desktop files in place and accessible through Orte; hide the icon layer.
    if (desktop.type === "org.kde.plasma.folder") {
        desktop.currentConfigGroup = ["General"];
        desktop.writeConfig("filterMode", "2");
        desktop.writeConfig("filterPattern", "*");
        desktop.reloadConfig();
    }
    // Primary screen gets the functional hub; other screens keep the artwork clear.
    if (desktop.screen !== 0) continue;
    var found = desktop.widgets().filter(function(w) { return w.type === "io.github.witzelfitz.hub"; });
    if (!found.length) {
        var screen = screenGeometry(desktop.screen);
        var w = Math.min(700, Math.max(360, screen.width * 0.46));
        var h = Math.min(750, Math.max(540, screen.height - 190));
        desktop.addWidget("io.github.witzelfitz.hub", 60, 65, w, h);
    }
    installed++;
}
var bars = panels();
for (var j = 0; j < bars.length; ++j) {
    bars[j].height = 52;
    bars[j].alignment = "center";
    bars[j].writeConfig("floating", "1");
}
if (!installed) throw new Error("Kein primärer KDE-Desktop gefunden.");
print("WITZELFITZ_OK");
