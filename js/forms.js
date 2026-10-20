/* ScanDriver forms. Both forms hand the details to WhatsApp (no backend). */
(function () {
  "use strict";

  var CUSTOMER_NUMBER = "919717498198";

  /* ---- Helpers ---- */
  function cleanPhone(value) {
    var digits = String(value || "").replace(/\D/g, "");
    if (digits.length === 12 && digits.indexOf("91") === 0) digits = digits.slice(2);
    if (digits.length === 11 && digits.charAt(0) === "0") digits = digits.slice(1);
    return digits;
  }

  function validPhone(value) {
    return /^[6-9]\d{9}$/.test(cleanPhone(value));
  }

  function openWhatsApp(lines) {
    var url = "https://wa.me/" + CUSTOMER_NUMBER + "?text=" + encodeURIComponent(lines.join("\n"));
    var win = window.open(url, "_blank", "noopener");
    if (!win) window.location.href = url;
  }

  function setError(field, message) {
    if (!field) return;
    var err = field.querySelector(".error");
    field.classList.toggle("field--error", Boolean(message));
    if (err) {
      err.textContent = message || "";
      err.hidden = !message;
    }
    field.querySelectorAll("input:not([type=radio]), select, textarea").forEach(function (c) {
      if (message) c.setAttribute("aria-invalid", "true");
      else c.removeAttribute("aria-invalid");
    });
  }

  function showStatus(el, message) {
    if (!el) return;
    el.textContent = message;
    el.hidden = !message;
  }

  /* ---- Booking form ----
     One form, five trip types. The trip type decides which fields show and in what order. */
  var booking = document.getElementById("booking-form");

  if (booking) {
    var POINT_TO_POINT = {
      fields: ["pickup", "drop", "distance", "location", "datetime", "comments"],
      pickup: ["Pickup city / location", "e.g. Connaught Place, Delhi"],
      pickupOptional: false
    };
    var LAYOUTS = {
      "Hourly": {
        fields: ["hours", "location", "datetime", "pickup", "comments"],
        pickup: ["Pickup location", "e.g. Sector 29, Gurgaon"],
        pickupOptional: false
      },
      "One way": POINT_TO_POINT,
      "Round trip": POINT_TO_POINT,
      "Outstation": POINT_TO_POINT,
      "Monthly": {
        fields: ["interview", "days", "perday", "location", "pickup", "comments"],
        pickup: ["Pickup location", "e.g. Sector 29, Gurgaon"],
        pickupOptional: true
      }
    };

    /* ?service=... links (from the services page) pick the closest trip type */
    var SERVICES = {
      hourly: ["Hourly driver", "Hourly"],
      daily: ["Daily driver", "Hourly"],
      weekly: ["Weekly driver", "Hourly"],
      monthly: ["Monthly driver", "Monthly"],
      outstation: ["Outstation driver", "Outstation"],
      corporate: ["Corporate driver", "Hourly"],
      airport: ["Airport transfer", "One way"],
      event: ["Event & wedding driver", "Hourly"],
      school: ["School pickup & drop driver", "Monthly"]
    };

    var f = booking.elements;
    var el = {
      name: f.name, phone: f.phone, service: f.service,
      hours: f.hours, date: f.date, time: f.time,
      pickup: f.pickup, drop: f.drop, distance: f.distance,
      idate: f.idate, itime: f.itime, days: f.days, perday: f.perday,
      comments: f.comments
    };
    var tripInputs = booking.querySelectorAll('input[name="trip"]');
    var carInputs = booking.querySelectorAll('input[name="car"]');
    var carField = booking.querySelector('[data-field="car"]');
    var lfNodes = booking.querySelectorAll("[data-lf]");
    var pickupText = document.getElementById("pickup-label-text");
    var pickupOpt = document.getElementById("pickup-opt");
    var whenLine = document.getElementById("when-line");
    var calLink = document.getElementById("cal-link");
    var previewList = document.getElementById("preview-list");
    var serviceNote = document.getElementById("service-note");
    var locBtn = document.getElementById("share-location");
    var locHint = document.getElementById("location-hint");
    var status = document.getElementById("booking-status");
    var locationLink = "";

    function lf(key) { return booking.querySelector('[data-lf="' + key + '"]'); }

    function checked(inputs) {
      for (var i = 0; i < inputs.length; i++) if (inputs[i].checked) return inputs[i];
      return null;
    }

    function currentTrip() {
      var t = checked(tripInputs);
      return t ? t.value : "Hourly";
    }

    function layout() { return LAYOUTS[currentTrip()]; }

    /* ---- Dates ---- */
    function pad(n) { return n < 10 ? "0" + n : String(n); }
    function dateStr(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
    function timeStr(d) { return pad(d.getHours()) + ":" + pad(d.getMinutes()); }

    function toDate(dv, tv) {
      if (!dv || !tv) return null;
      var d = new Date(dv + "T" + tv);
      return isNaN(d.getTime()) ? null : d;
    }

    function fmtDateTime(d) {
      if (!d) return "";
      return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) + ", " +
        d.toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true });
    }

    function fmtShort(d) {
      if (!d) return "";
      return d.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" }) + " at " +
        d.toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true });
    }

    function calStamp(d) {
      return d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + "T" + pad(d.getHours()) + pad(d.getMinutes()) + "00";
    }

    /* Start with a slot an hour from now, rounded up to the next quarter hour */
    (function setDefaults() {
      var d = new Date(Date.now() + 60 * 60000);
      d.setMinutes(Math.ceil(d.getMinutes() / 15) * 15, 0, 0);
      el.date.min = el.idate.min = dateStr(new Date());
      el.date.value = el.idate.value = dateStr(d);
      el.time.value = el.itime.value = timeStr(d);
    })();

    /* ---- Values ---- */
    function values() {
      var car = checked(carInputs);
      return {
        service: el.service.value,
        trip: currentTrip(),
        car: car ? car.getAttribute("data-label") : "",
        name: el.name.value.trim(),
        phone: cleanPhone(el.phone.value),
        hours: el.hours.value.trim(),
        pickup: el.pickup.value.trim(),
        drop: el.drop.value.trim(),
        distance: el.distance.value,
        when: toDate(el.date.value, el.time.value),
        interview: toDate(el.idate.value, el.itime.value),
        days: el.days.value.trim(),
        perday: el.perday.value.trim(),
        location: locationLink,
        comments: el.comments.value.trim()
      };
    }

    /* ---- Live preview ---- */
    function previewRows(v, L) {
      var rows = [];
      if (v.service) rows.push(["Service", v.service]);
      rows.push(["Trip type", v.trip]);
      rows.push(["Car type", v.car]);
      rows.push(["Name", v.name]);
      rows.push(["WhatsApp", v.phone ? "+91 " + v.phone : ""]);
      L.fields.forEach(function (key) {
        if (key === "hours") rows.push(["Hours needed", v.hours]);
        else if (key === "pickup") rows.push(["Pickup", v.pickup]);
        else if (key === "drop") rows.push(["Drop", v.drop]);
        else if (key === "distance") rows.push(["Distance", v.distance ? "About " + v.distance + " km (one way)" : ""]);
        else if (key === "datetime") rows.push(["Date and time", fmtDateTime(v.when)]);
        else if (key === "interview") rows.push(["Interview", fmtDateTime(v.interview)]);
        else if (key === "days") rows.push(["Working days", v.days ? v.days + " per month" : ""]);
        else if (key === "perday") rows.push(["Hours per day", v.perday]);
      });
      return rows;
    }

    function updateInterview(v) {
      if (!whenLine || !calLink) return;
      var start = v.interview;
      whenLine.textContent = start ? fmtShort(start) : "Choose an interview date and start time";
      if (!start) return;
      var end = new Date(start.getTime() + 60 * 60000);
      var params = [
        "action=TEMPLATE",
        "text=" + encodeURIComponent("ScanDriver driver interview"),
        "dates=" + calStamp(start) + "/" + calStamp(end),
        "details=" + encodeURIComponent("Face-to-face trial with the driver candidate for a monthly contract, arranged through ScanDriver."),
        "ctz=Asia/Kolkata"
      ];
      if (v.pickup) params.push("location=" + encodeURIComponent(v.pickup));
      calLink.href = "https://calendar.google.com/calendar/render?" + params.join("&");
    }

    function render() {
      var v = values();
      var rows = previewRows(v, layout());
      previewList.textContent = "";
      rows.forEach(function (r) {
        var wrap = document.createElement("div");
        var dt = document.createElement("dt");
        var dd = document.createElement("dd");
        dt.textContent = r[0];
        dd.textContent = r[1] ? r[1] : "Not added yet";
        dd.setAttribute("data-empty", r[1] ? "false" : "true");
        wrap.appendChild(dt);
        wrap.appendChild(dd);
        previewList.appendChild(wrap);
      });
      updateInterview(v);
    }

    /* ---- Layout per trip type ---- */
    function applyLayout() {
      var L = layout();
      lfNodes.forEach(function (node) {
        var i = L.fields.indexOf(node.getAttribute("data-lf"));
        node.hidden = i < 0;
        node.style.order = i < 0 ? "" : String(i);
        if (i < 0) setError(node, "");
      });
      pickupText.textContent = L.pickup[0];
      pickupOpt.textContent = L.pickupOptional ? " (optional)" : "";
      el.pickup.placeholder = L.pickup[1];
    }

    /* ---- Prefill from a services link ---- */
    try {
      var key = new URLSearchParams(window.location.search).get("service");
      if (key && SERVICES[key]) {
        el.service.value = SERVICES[key][0];
        tripInputs.forEach(function (input) { input.checked = input.value === SERVICES[key][1]; });
        serviceNote.textContent = "Booking: " + SERVICES[key][0];
        serviceNote.hidden = false;
      }
    } catch (e) { /* older browser: skip prefill */ }

    booking.addEventListener("input", render);
    booking.addEventListener("change", function (e) {
      if (e.target && e.target.name === "trip") {
        applyLayout();
        showStatus(status, "");
      }
      render();
    });

    /* ---- Optional location sharing ---- */
    if (locBtn) {
      locBtn.addEventListener("click", function () {
        if (!navigator.geolocation) {
          locHint.textContent = "This browser can't share location. Type the pickup address instead.";
          return;
        }
        locBtn.disabled = true;
        locHint.textContent = "Getting your location...";
        navigator.geolocation.getCurrentPosition(
          function (pos) {
            locationLink = "https://maps.google.com/?q=" + pos.coords.latitude.toFixed(6) + "," + pos.coords.longitude.toFixed(6);
            locBtn.disabled = false;
            locBtn.setAttribute("data-state", "done");
            locBtn.querySelector("span").textContent = "Location shared";
            locHint.textContent = "Your location link will be included in the WhatsApp message.";
          },
          function () {
            locBtn.disabled = false;
            locHint.textContent = "Location access was blocked. Allow it in your browser settings, or type the pickup address instead.";
          },
          { enableHighAccuracy: true, timeout: 12000 }
        );
      });
    }

    /* ---- Validation ---- */
    function num(s) { return s === "" ? NaN : Number(s); }

    function whenError(d, missing, past) {
      if (!d) return missing;
      if (d.getTime() < Date.now() - 5 * 60000) return past;
      return "";
    }

    var CHECKS = {
      hours: function (v) {
        var n = num(v.hours);
        return n >= 2 && n <= 24 ? "" : "Enter total hours, from 2 to 24.";
      },
      pickup: function (v, L) { return v.pickup || L.pickupOptional ? "" : "Enter the pickup location."; },
      drop: function (v) { return v.drop ? "" : "Enter the drop city or location."; },
      distance: function (v) { return v.distance ? "" : "Choose the estimated distance."; },
      datetime: function (v) {
        return whenError(v.when, "Choose the date and time you need the driver.", "Choose a date and time in the future.");
      },
      interview: function (v) {
        return whenError(v.interview, "Choose the interview date and start time.", "Choose an interview time in the future.");
      },
      days: function (v) {
        var n = num(v.days);
        return n >= 1 && n <= 31 && n % 1 === 0 ? "" : "Enter working days per month, from 1 to 31.";
      },
      perday: function (v) {
        var n = num(v.perday);
        return n >= 1 && n <= 24 ? "" : "Enter hours per day, from 1 to 24.";
      }
    };

    function validate(v, L) {
      var firstBad = null;

      function flag(node, control, message) {
        setError(node, message);
        if (message && !firstBad) firstBad = control;
      }

      flag(el.name.closest(".field"), el.name, v.name ? "" : "Enter your name.");
      flag(el.phone.closest(".field"), el.phone, validPhone(el.phone.value) ? "" : "Enter a 10-digit WhatsApp number, like 98765 43210.");
      flag(carField, carInputs[0], v.car ? "" : "Choose a car type.");

      L.fields.forEach(function (key) {
        var node = lf(key);
        var check = CHECKS[key];
        flag(node, node.querySelector("input, select, textarea"), check ? check(v, L) : "");
      });
      return firstBad;
    }

    /* ---- Send ---- */
    booking.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = values();
      var L = layout();
      var firstBad = validate(v, L);

      if (firstBad) {
        showStatus(status, "Please fix the highlighted fields and send again.");
        firstBad.focus();
        return;
      }
      showStatus(status, "Opening WhatsApp with your booking details...");

      var lines = ["Hi ScanDriver! I'd like to book a driver.", ""];
      if (v.service) lines.push("Service: " + v.service);
      lines.push("Trip type: " + v.trip);
      lines.push("Car type: " + v.car);
      lines.push("Name: " + v.name);
      lines.push("WhatsApp: +91 " + v.phone);
      L.fields.forEach(function (k) {
        if (k === "hours") lines.push("Hours required: " + v.hours);
        else if (k === "pickup" && v.pickup) lines.push("Pickup: " + v.pickup);
        else if (k === "drop") lines.push("Drop: " + v.drop);
        else if (k === "distance") lines.push("Distance: About " + v.distance + " km (one way)");
        else if (k === "datetime") lines.push("Date and time: " + fmtDateTime(v.when));
        else if (k === "interview") lines.push("Interview (face-to-face trial): " + fmtDateTime(v.interview));
        else if (k === "days") lines.push("Working days per month: " + v.days);
        else if (k === "perday") lines.push("Hours per day: " + v.perday);
        else if (k === "location" && v.location) lines.push("My location: " + v.location);
        else if (k === "comments" && v.comments) lines.push("Comments: " + v.comments);
      });
      openWhatsApp(lines);
    });

    applyLayout();
    render();
  }

  /* ---- Enquiry form ---- */
  var enquiry = document.getElementById("enquiry-form");

  if (enquiry) {
    var eName = enquiry.elements.name;
    var ePhone = enquiry.elements.phone;
    var eMsg = enquiry.elements.message;
    var eStatus = document.getElementById("enquiry-status");

    enquiry.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstBad = null;

      function check(control, message) {
        setError(control.closest(".field"), message);
        if (message && !firstBad) firstBad = control;
      }

      check(eName, eName.value.trim() ? "" : "Enter your full name.");
      check(ePhone, validPhone(ePhone.value) ? "" : "Enter a 10-digit phone number, like 98765 43210.");

      if (firstBad) {
        showStatus(eStatus, "Please fix the highlighted fields and send again.");
        firstBad.focus();
        return;
      }
      showStatus(eStatus, "Opening WhatsApp with your enquiry...");

      var lines = ["Hi ScanDriver! I'd like to send an enquiry.", ""];
      lines.push("Name: " + eName.value.trim());
      lines.push("Phone: +91 " + cleanPhone(ePhone.value));
      if (eMsg.value.trim()) lines.push("Requirements: " + eMsg.value.trim());
      openWhatsApp(lines);
    });
  }
})();
