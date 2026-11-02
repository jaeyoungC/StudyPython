// 할 일 화면 (21단원). 빌드 도구 없이 브라우저가 그대로 읽는 자바스크립트입니다.
//
// 구조는 세 부분뿐입니다.
//   1. state  — 화면이 보여 줄 모든 것 (토큰, 할 일 목록, 필터, 오류)
//   2. render — state 를 읽어 DOM 을 다시 그린다. state 를 바꾸지 않는다.
//   3. 이벤트 — 사용자가 한 일 → API 호출 → state 변경 → render()
// "DOM 을 직접 고치지 말고 state 를 고친 뒤 render 한다"가 규칙입니다. 그래야 화면과 데이터가 어긋나지 않습니다.

const API = "http://127.0.0.1:8000";

const state = {
  token: localStorage.getItem("token"), // 새로고침해도 로그인 유지. 보안상 대가는 README 질문 4
  tasks: [],
  filter: "all",
  error: "",
};

// --- API 호출 -----------------------------------------------------------------

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
  const response = await fetch(API + path, { ...options, headers });
  if (response.status === 204) return null;
  const body = await response.json();
  if (!response.ok) {
    // 17단원의 오류 봉투 {"error": {"code", "message"}} 를 그대로 예외로
    const error = new Error(body.error?.message || response.statusText);
    error.code = body.error?.code;
    error.status = response.status;
    throw error;
  }
  return body;
}

async function loadTasks() {
  const params = new URLSearchParams({ limit: "100" });
  if (state.filter !== "all") params.set("done", String(state.filter === "done"));
  const page = await api(`/tasks?${params}`); // 페이지는 첫 장만. 다음 장(next_cursor)은 "더 깊이"
  state.tasks = page.items;
}

// --- 렌더링: state → DOM ----------------------------------------------------------

const $ = (selector) => document.querySelector(selector);

function render() {
  $("#status").textContent = state.error;
  const loggedIn = Boolean(state.token);
  $("#auth-section").classList.toggle("hidden", loggedIn);
  $("#tasks-section").classList.toggle("hidden", !loggedIn);

  const list = $("#task-list");
  list.replaceChildren(); // 전부 지우고 다시 그린다. 느려지면 그때 가서 차이만 갱신한다 (README 더 깊이)
  for (const task of state.tasks) {
    const item = document.createElement("li");
    item.classList.toggle("done", task.done);

    const title = document.createElement("span");
    title.className = "title";
    title.textContent = task.title; // innerHTML 이 아니라 textContent: 제목에 <script> 가 들어 있어도 글자로만 보인다

    const complete = document.createElement("button");
    complete.type = "button";
    complete.textContent = "완료";
    complete.disabled = task.done;
    complete.setAttribute("aria-label", `${task.title} 완료`);
    complete.addEventListener("click", () => withErrors(async () => {
      await api(`/tasks/${task.id}/complete`, { method: "POST" });
      await loadTasks();
    }));

    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "삭제";
    remove.setAttribute("aria-label", `${task.title} 삭제`);
    remove.addEventListener("click", () => withErrors(async () => {
      await api(`/tasks/${task.id}`, { method: "DELETE" });
      await loadTasks();
    }));

    item.append(title, complete, remove);
    list.append(item);
  }
}

// 모든 이벤트 핸들러는 이 함수로 감싼다: 성공하면 오류를 지우고, 실패하면 오류를 state 에 넣고, 어느 쪽이든 render.
async function withErrors(action) {
  try {
    state.error = "";
    await action();
  } catch (error) {
    if (error.status === 401) {
      state.token = null;
      localStorage.removeItem("token");
      state.tasks = [];
    }
    state.error = error.message;
  }
  render();
}

// --- 이벤트 ---------------------------------------------------------------------

$("#auth-form").addEventListener("submit", (event) => {
  event.preventDefault(); // 폼의 기본 동작(페이지 이동)을 막는다. Enter 키로도 submit 이 일어나므로 키보드만으로 로그인된다
  const form = new FormData(event.target);
  withErrors(async () => {
    const body = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username: form.get("username"), password: form.get("password") }),
    });
    state.token = body.access_token;
    localStorage.setItem("token", state.token);
    await loadTasks();
  });
});

$("#register-button").addEventListener("click", () => {
  const form = new FormData($("#auth-form"));
  withErrors(async () => {
    await api("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username: form.get("username"), password: form.get("password") }),
    });
    state.error = "가입했습니다. 로그인하세요.";
  });
});

$("#add-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = $("#title");
  withErrors(async () => {
    await api("/tasks", { method: "POST", body: JSON.stringify({ title: input.value }) });
    input.value = "";
    input.focus(); // 추가한 뒤 바로 다음 것을 칠 수 있게 포커스를 돌려준다
    await loadTasks();
  });
});

$("#filter").addEventListener("change", (event) => {
  state.filter = event.target.value;
  withErrors(loadTasks);
});

$("#logout-button").addEventListener("click", () => {
  state.token = null;
  localStorage.removeItem("token");
  state.tasks = [];
  render();
});

// 첫 화면
withErrors(async () => {
  if (state.token) await loadTasks();
});
