/* Family Jigsaw Puzzles: shared page behaviour (wordmark, look and backdrop preview, sign-up forms). */
(function () {
  "use strict";
  var F = window.FJP;
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  // Wordmark: colour each letter like the pages of the family ABC book.
  $$(".wordmark").forEach(function (el) {
    var i = 0;
    el.innerHTML = el.textContent.trim().split(" ").map(function (word) {
      return '<span class="w">' + word.split("").map(function (ch) { i++; return '<span class="l" style="--i:' + i + '">' + F.esc(ch) + "</span>"; }).join("") + "</span>";
    }).join(" ");
  });

  // Looks and backdrops: switch the example puzzle (our own drawing) between treatments and scenes.
  var pic = $(".looks-pic .puzzle");
  function press(attr, btn) {
    $$("[" + attr + "]").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
  }
  $$("[data-look]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-look");
      press("data-look", btn);
      pic.setAttribute("class", "puzzle look-" + id);
      $$("[data-line]").forEach(function (p) { p.hidden = p.getAttribute("data-line") !== id; });
      var sel = $("#w-look"); if (sel) sel.value = id;
    });
  });
  $$("[data-bd]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-bd");
      press("data-bd", btn);
      $$(".bd", pic).forEach(function (g) {
        if (g.classList.contains("bd-" + id)) g.removeAttribute("hidden"); else g.setAttribute("hidden", "");
      });
    });
  });

  // "Notify me" on a size picks it in the sign-up form.
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-want]"); if (!a) return;
    var sel = $("#w-want"); if (sel) sel.value = a.dataset.want;
    setTimeout(function () { var em = $("#w-email"); if (em) em.focus({ preventScroll: true }); }, 400);
  });

  // Sign-up forms
  $$("form[data-signup]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = $(".form-msg", form), data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data.form = form.dataset.signup;
      if (!data.email || !/^\S+@\S+\.\S+$/.test(data.email)) { msg.textContent = "Please enter an email address like name@example.com."; return; }
      var btn = $("button[type=submit]", form); if (btn) btn.disabled = true;
      send(data).then(function (sent) {
        if (btn) btn.disabled = false;
        msg.textContent = sent ? "You're on the list. We'll email you when ordering opens." : "Sorry, that didn't go through. Please try again, or email " + F.config.email + ".";
        if (sent) form.reset();
      });
    });
  });

  function send(data) {
    if (!F.config.formEndpoint) return Promise.resolve(false);
    var body = Object.assign({
      _subject: "Family Jigsaw Puzzles waitlist: " + (data.size || "any size") + ", " + (data.material || ""),
      _template: "table",
      _replyto: data.email,
      site: "familyjigsawpuzzles.com",
      region: F.region
    }, data);
    return fetch(F.config.formEndpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { return r.ok ? r.json().then(function (j) { return String(j.success) === "true"; }, function () { return true; }) : false; })
      .catch(function () { return false; });
  }

  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
