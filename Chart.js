/* chart.js – Temperature + Leak Sensor from ThingSpeak (Dual Axis + Status Indicators) */

const config = {
  channel: 3190908, // <--- LAITA TÄHÄN OMA CHANNEL ID
  fields: [1, 2], // 1 = lämpötila, 2 = leak ADC

  fieldLabels: {
    1: "Temperature (°C)",
    2: "Leak Sensor (ADC Value)",
  },

  readApiKey: "74G2AEEXLEDEN477",
  results: 300,
  refreshIntervalSec: 60,

  chartTitle: "Temperature & Leak Sensor – ThingSpeak",

  chartOptions: {
    curveType: "function",
    legend: { position: "bottom" },
    explorer: { axis: "horizontal", keepInBounds: true },

    // --- DUAL AXIS ---
    series: {
      0: { targetAxisIndex: 0, color: "#e74c3c" }, // temperature = left
      1: { targetAxisIndex: 1, color: "#f39c12" }, // leak = right
    },

    vAxes: {
      0: { title: "Temperature (°C)" },
      1: { title: "Leak Sensor (ADC Value)" },
    },
  },
};

// --- ALERT LIMITS ---
const tempLimit = 50; // °C
const leakLimit = 40000; // ADC
let currentRange = "day";

(function () {
  google.charts.load("current", { packages: ["corechart"] });
  google.charts.setOnLoadCallback(init);

  async function init() {
    function setActiveButton(id) {
      document.querySelectorAll("#range_buttons button").forEach((btn) => {
        btn.classList.remove("active");
      });
      document.getElementById(id).classList.add("active");
    }

    document.getElementById("btn_day").addEventListener("click", () => {
      currentRange = "day";
      setActiveButton("btn_day");
      fetchAndDraw();
    });

    document.getElementById("btn_week").addEventListener("click", () => {
      currentRange = "week";
      setActiveButton("btn_week");
      fetchAndDraw();
    });

    document.getElementById("btn_month").addEventListener("click", () => {
      currentRange = "month";
      setActiveButton("btn_month");
      fetchAndDraw();
    });

    await fetchAndDraw();

    if (config.refreshIntervalSec > 0) {
      setInterval(fetchAndDraw, config.refreshIntervalSec * 1000);
    }
  }

  function formatDateForThingSpeak(date) {
    const p = (n) => (n < 10 ? "0" + n : n);
    return (
      date.getFullYear() +
      "-" +
      p(date.getMonth() + 1) +
      "-" +
      p(date.getDate()) +
      "%20" +
      p(date.getHours()) +
      ":" +
      p(date.getMinutes()) +
      ":" +
      p(date.getSeconds())
    );
  }

  async function fetchAndDraw() {
    const statusEl = document.getElementById("chart_status");
    const chartEl = document.getElementById("curve_chart");
    const alertEl = document.getElementById("alert_indicator");

    const now = new Date();
    const timeStr = now.toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    statusEl.textContent = `Checking for updates... (${timeStr})`;

    try {
      const end = formatDateForThingSpeak(now);
      const startDate = new Date(now);

      if (currentRange === "day") startDate.setDate(now.getDate() - 1);
      if (currentRange === "week") startDate.setDate(now.getDate() - 7);
      if (currentRange === "month") startDate.setMonth(now.getMonth() - 1);

      const start = formatDateForThingSpeak(startDate);

      const url =
        `https://api.thingspeak.com/channels/${config.channel}/feeds.json?` +
        `start=${start}&end=${end}` +
        (config.readApiKey ? `&api_key=${config.readApiKey}` : "") +
        `&results=${config.results}`;

      const res = await fetch(url);
      const json = await res.json();

      if (!json.feeds || json.feeds.length === 0) {
        chartEl.innerHTML = `
            <div style="
              display:flex;flex-direction:column;justify-content:center;align-items:center;
              height:400px;color:#555;background:#fafafa;border-radius:12px;">
              <p style="font-size:1.2em;font-weight:bold;">No recent data available</p>
              <p>The chart will update automatically when new data arrives.</p>
            </div>`;
        statusEl.textContent = `No data available (last checked: ${timeStr})`;
        return;
      }

      const dataTable = new google.visualization.DataTable();
      dataTable.addColumn("datetime", "Time");

      config.fields.forEach((f) => {
        dataTable.addColumn("number", config.fieldLabels[f]);
      });

      json.feeds.forEach((feed) => {
        const t = new Date(feed.created_at);
        const row = [t];

        config.fields.forEach((f) => {
          const v = parseFloat(feed[`field${f}`]);
          row.push(isNaN(v) ? null : v);
        });

        dataTable.addRow(row);
      });

      // ---- Latest values ----
      const latest = json.feeds[json.feeds.length - 1];
      const temp = parseFloat(latest.field1);
      const leak = parseFloat(latest.field2);

      const dynamicTitle = `${config.chartTitle} — ${temp.toFixed(
        1
      )}°C / Leak: ${leak}`;

      const options = Object.assign(
        {
          title: dynamicTitle,
          hAxis: {
            title: "Time",
            format: "HH:mm",
            slantedText: true,
            slantedTextAngle: 45,
          },
          interpolateNulls: true,
        },
        config.chartOptions
      );

      const chart = new google.visualization.LineChart(chartEl);
      chart.draw(dataTable, options);

      statusEl.textContent = `Showing ${dataTable.getNumberOfRows()} datapoints.`;

      //
      // ---- STATUS PANEL (Temperature + Leak) ----
      //
      let tempStatus = "";
      let leakStatus = "";

      if (temp > tempLimit) {
        tempStatus = `<span style="color:red;">Temperature: OVERHEAT (${temp.toFixed(
          1
        )}°C)</span>`;
      } else {
        tempStatus = `<span style="color:green;">Temperature: Normal (${temp.toFixed(
          1
        )}°C)</span>`;
      }

      if (leak > leakLimit) {
        leakStatus = `<span style="color:red;">Leak Detector: LEAK DETECTED (ADC ${leak})</span>`;
      } else {
        leakStatus = `<span style="color:green;">Leak Detector: OK (ADC ${leak})</span>`;
      }

      alertEl.innerHTML = `${tempStatus}<br>${leakStatus}`;

      //
      // ---- Last updated timestamp ---
      //
      const lastUpdateEl = document.getElementById("last_update");
      if (lastUpdateEl) {
        const dateStr = now.toLocaleDateString("en-EN", {
          weekday: "short",
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
        });
        lastUpdateEl.textContent = `Updated: ${dateStr} klo ${timeStr}`;
      }
    } catch (err) {
      console.error(err);
      statusEl.textContent = "Error retrieving data: " + err.message;
    }
  }
})();
