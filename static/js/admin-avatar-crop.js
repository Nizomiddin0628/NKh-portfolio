/* Admin: crop the portrait right after choosing it.
   Writes "x,y,width,height" (pixels of the original) into the hidden
   avatar_crop field; the server cuts the image on save. The original file is
   kept, so the crop can be changed later without uploading again. */
(function () {
  "use strict";

  function init() {
    var input = document.querySelector('input[type="file"][name="avatar"]');
    var hidden = document.querySelector('input[name="avatar_crop"]');
    if (!input || !hidden || !window.Cropper) return;

    var holder = input.parentNode;
    var wrap = document.createElement("div");
    wrap.style.cssText = "margin-top:12px;max-width:420px";
    wrap.innerHTML =
      '<p class="help" style="margin:0 0 8px">Drag and zoom to choose what is visible (4:5 portrait). ' +
      'Saved together with the form.</p>' +
      '<div style="max-height:520px;background:#111;border-radius:8px;overflow:hidden"><img alt="" style="display:block;max-width:100%"></div>' +
      '<button type="button" class="button" style="margin-top:8px">Reset crop</button>';
    holder.parentNode.insertBefore(wrap, holder.nextSibling);

    var img = wrap.querySelector("img");
    var reset = wrap.querySelector("button");
    var cropper = null;

    function save() {
      if (!cropper) return;
      var d = cropper.getData(true);
      hidden.value = [d.x, d.y, d.width, d.height].join(",");
    }

    function start(src, restore) {
      wrap.hidden = false;
      if (cropper) { cropper.destroy(); cropper = null; }
      img.onload = function () {
        cropper = new Cropper(img, {
          aspectRatio: 4 / 5,
          viewMode: 1,
          autoCropArea: 0.9,
          checkOrientation: false,
          rotatable: false,
          background: false,
          ready: function () {
            var p = (restore || "").split(",").map(Number);
            if (p.length === 4 && p.every(isFinite)) {
              cropper.setData({ x: p[0], y: p[1], width: p[2], height: p[3] });
            }
            save();
          },
          crop: save,
        });
      };
      img.src = src;
    }

    var current = holder.querySelector("a[href]");
    if (current) start(current.href, hidden.value);
    else wrap.hidden = true;

    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) return;
      hidden.value = "";
      start(URL.createObjectURL(file), "");
    });

    reset.addEventListener("click", function () {
      if (cropper) { cropper.reset(); save(); }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
