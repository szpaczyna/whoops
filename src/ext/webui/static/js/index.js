import { API } from "./api.js";

function showAlert(message, type = "success") {
  const alertContainer = document.querySelector("#error-container");
  alertContainer.innerHTML = "";

  const div = document.createElement("div");
  div.className = `alert alert-${type} mt-2`;
  div.role = "alert";
  div.textContent = message;
  alertContainer.appendChild(div);
}

document.addEventListener("DOMContentLoaded", () => {
  const wait = document.querySelector(".wait");
  const importBtn = document.getElementById("import-button");
  const scheduleBtn = document.getElementById("schedule-button");
  const unscheduleBtn = document.getElementById("unschedule-button");

  importBtn.addEventListener("click", async () => {
    importBtn.disabled = true;
    wait.style.visibility = "visible";

    const result = await API.importNow();
    showAlert(result.message, result.success ? "success" : "danger");

    importBtn.disabled = false;
    wait.style.visibility = "hidden";


    fetchImportStatus();
  });

  scheduleBtn.addEventListener("click", async () => {
    const hour = document.getElementById("hour-input").value;
    const minute = document.getElementById("minute-input").value || "0";

    const result = await API.scheduleImport(hour, minute);
    showAlert(result.message, result.success ? "success" : "danger");
    fetchImportStatus();
  });

  unscheduleBtn.addEventListener("click", async () => {
    const result = await API.deleteSchedule();
    showAlert(result.message, result.success ? "success" : "danger");
    fetchImportStatus();
  });

  fetchImportStatus({ prefill: true });
  startPolling();
});


function pad(value) {
  return String(value).padStart(2, "0");
}

function renderSchedule(schedule, prefill) {
  const label = document.getElementById("schedule-label");
  const unscheduleBtn = document.getElementById("unschedule-button");

  if (schedule) {
    label.textContent = `Daily import: ${pad(schedule.hour)}:${pad(schedule.minute)} UTC`;
    unscheduleBtn.style.display = "";
  } else {
    label.textContent = "No daily import";
    unscheduleBtn.style.display = "none";
  }

  if (prefill && schedule) {
    document.getElementById("hour-input").value = schedule.hour;
    document.getElementById("minute-input").value = schedule.minute;
  }
}

async function fetchImportStatus({ prefill = false } = {}) {
  const result = await API.getImportStatus();

  if (!result.success) {
    console.error(result.message);
    return;
  }

  const { backlog, last_status, schedule } = result.data;
  renderSchedule(schedule, prefill);

  const backlogBadge = document.getElementById("backlog-badge");
  const statusBadge = document.getElementById("status-badge");

  backlogBadge.textContent = backlog ?? 0;
  statusBadge.textContent = last_status ?? "N/A";

  if (backlog > 0) {
    backlogBadge.classList.remove("badge-primary");
    backlogBadge.classList.add("badge-warning");
  } else {
    backlogBadge.classList.remove("badge-warning");
    backlogBadge.classList.add("badge-primary");
  }
}

let statusInterval;

function startPolling() {
  let running = false;

  statusInterval = setInterval(async () => {
    if (running) return;
    running = true;
    await fetchImportStatus();
    running = false;
  }, 5000);
}

