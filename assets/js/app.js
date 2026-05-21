document.addEventListener("DOMContentLoaded", async () => {
  const page = document.body.dataset.page || "generic";
  const USER_KEY = "fitdiscipline_user_id";

  const qs = (selector) => document.querySelector(selector);
  const qsa = (selector) => Array.from(document.querySelectorAll(selector));

  const setOutput = (selector, data) => {
    const el = qs(selector);
    if (!el) return;
    if (typeof data === "string") {
      el.textContent = data;
      return;
    }
    el.textContent = JSON.stringify(data, null, 2);
  };

  const toNum = (value) => (value === "" || value === null || value === undefined ? null : Number(value));
  const calculateAge = (birthDate) => {
    if (!birthDate) return null;
    const dob = new Date(birthDate);
    if (Number.isNaN(dob.getTime())) return null;
    const today = new Date();
    let age = today.getFullYear() - dob.getFullYear();
    const m = today.getMonth() - dob.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
      age -= 1;
    }
    return age >= 0 ? age : null;
  };

  const api = async (url, method = "GET", body = null) => {
    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body !== null) options.body = JSON.stringify(body);
    const response = await fetch(url, options);
    const json = await response.json();
    if (!response.ok) {
      throw new Error(json.message || json.detail || "Request failed");
    }
    return json;
  };

  let sessionUserId = "";
  let sessionUser = null;

  const saveUserId = (userId) => {
    if (!userId) return;
    localStorage.setItem(USER_KEY, userId);
    sessionUserId = userId;
  };

  const loadUserId = () => sessionUserId || localStorage.getItem(USER_KEY) || "";

  const lockUserInput = (selector, userId) => {
    const input = qs(selector);
    if (!input) return;
    input.value = userId;
    input.readOnly = true;
  };

  const hydrateUserInputs = () => {
    const userId = loadUserId();
    if (!userId) return;

    qsa("input[name='user_id']").forEach((el) => {
      el.value = userId;
      el.readOnly = true;
    });
    lockUserInput("#review-user-id", userId);
    lockUserInput("#activate-workout-user-id", userId);
    lockUserInput("#activate-meal-user-id", userId);
    lockUserInput("#ctx-user-id", userId);
  };

  const syncSessionUser = async () => {
    try {
      const data = await api("/api/auth/me");
      sessionUser = data?.data?.user || null;
      const userId = sessionUser?.user_id;
      if (!userId) return;
      saveUserId(userId);
      hydrateUserInputs();
    } catch (error) {
      if (window.location.pathname !== "/user/login") {
        window.location.href = "/user/login";
      }
    }
  };

  const withError = async (fn, outputSelector) => {
    try {
      await fn();
    } catch (error) {
      setOutput(outputSelector, { error: error.message });
    }
  };

  await syncSessionUser();

  if (page === "dashboard") {
    const ctxUser = qs("#ctx-user-id");
    const info = qs("#ctx-user-info");
    if (ctxUser) ctxUser.value = loadUserId();
    if (info) info.textContent = loadUserId() ? `User aktif: ${loadUserId()}` : "Belum ada user aktif";

    const saveBtn = qs("#btn-save-user-id");
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.title = "User ID mengikuti session login";
    }

    qs("#btn-db-health")?.addEventListener("click", async () => {
      await withError(async () => {
        const data = await api("/api/system/health/db");
        setOutput("#db-health-output", data);
      }, "#db-health-output");
    });
  }

  if (page === "onboarding") {
    const panels = qsa(".coach-panel");
    const dots = qsa(".coach-step-dot");
    const backBtn = qs("#onboarding-back");
    const nextBtn = qs("#onboarding-next");
    const submitBtn = qs("#onboarding-submit");
    const stepLabel = qs("#onboarding-step-label");
    let step = 1;

    const renderStep = () => {
      panels.forEach((panel) => panel.classList.toggle("active", Number(panel.dataset.step) === step));
      dots.forEach((dot, index) => dot.classList.toggle("active", index < step));
      if (stepLabel) stepLabel.textContent = `Step ${step}/8`;
      if (backBtn) backBtn.disabled = step === 1;
      if (nextBtn) nextBtn.classList.toggle("d-none", step === 8);
      if (submitBtn) submitBtn.classList.toggle("d-none", step !== 8);
    };

    nextBtn?.addEventListener("click", () => {
      if (step < 8) step += 1;
      renderStep();
    });

    backBtn?.addEventListener("click", () => {
      if (step > 1) step -= 1;
      renderStep();
    });

    const fillOnboardingProfile = () => {
      if (!sessionUser) return;
      const age = calculateAge(sessionUser.birth_date);
      setOutput("#onboarding-profile-name", sessionUser.name || "-");
      setOutput("#onboarding-profile-email", sessionUser.email || "-");
      setOutput("#onboarding-profile-age", age !== null ? `Umur: ${age}` : "Umur: -");
      setOutput("#onboarding-profile-gender", `Gender: ${sessionUser.gender || "-"}`);
      setOutput("#onboarding-profile-height", `Tinggi: ${sessionUser.height_cm ?? "-"} cm`);
    };

    const foodPrefList = qs("#food-pref-list");
    const addFoodPrefBtn = qs("#btn-add-food-pref");

    const createFoodPrefRow = () => {
      const row = document.createElement("div");
      row.className = "row g-2 food-pref-row";
      row.innerHTML = `
        <div class="col-md-5"><input class="form-control" data-food-name placeholder="Contoh: udang, seledri, daun bawang" /></div>
        <div class="col-md-3">
          <select class="form-select" data-food-category>
            <option value="allergy">Alergi</option>
            <option value="disliked">Tidak suka</option>
            <option value="intolerance">Intoleransi</option>
            <option value="religious">Religius</option>
            <option value="liked">Disukai</option>
          </select>
        </div>
        <div class="col-md-3">
          <select class="form-select" data-food-severity>
            <option value="hard">Wajib hindari</option>
            <option value="soft">Prefer hindari</option>
          </select>
        </div>
        <div class="col-md-1 d-grid">
          <button type="button" class="btn btn-outline-danger btn-remove-food-pref" title="Hapus">-</button>
        </div>
      `;
      return row;
    };

    addFoodPrefBtn?.addEventListener("click", () => {
      if (!foodPrefList) return;
      foodPrefList.appendChild(createFoodPrefRow());
    });

    foodPrefList?.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("btn-remove-food-pref")) return;
      const rows = qsa(".food-pref-row");
      const row = target.closest(".food-pref-row");
      if (!row) return;
      if (rows.length <= 1) {
        const input = row.querySelector("[data-food-name]");
        if (input instanceof HTMLInputElement) {
          input.value = "";
        }
        return;
      }
      row.remove();
    });

    fillOnboardingProfile();
    renderStep();

    qs("#onboarding-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      const userId = loadUserId();
      if (!userId) {
        setOutput("#onboarding-output", { error: "Session user tidak ditemukan. Silakan login ulang." });
        return;
      }

      const preferencesPayload = {
        sleep_target_hours: toNum(form.sleep_target_hours.value),
        activity_level: form.activity_level.value,
        goal_type: form.goal_type.value,
        goal_weight_kg: toNum(form.goal_weight_kg.value),
        goal_deadline_date: form.goal_deadline_date.value || null,
      };

      const fitnessPayload = {
        source: "onboarding",
        fitness_level: 1,
        body_weight_kg: toNum(form.body_weight_kg.value),
      };
      const foodPreferencePayloads = qsa(".food-pref-row")
        .map((row) => {
          const foodNameInput = row.querySelector("[data-food-name]");
          const categorySelect = row.querySelector("[data-food-category]");
          const severitySelect = row.querySelector("[data-food-severity]");
          const foodName = foodNameInput instanceof HTMLInputElement ? foodNameInput.value.trim() : "";
          const category = categorySelect instanceof HTMLSelectElement ? categorySelect.value : "disliked";
          const severity = severitySelect instanceof HTMLSelectElement ? severitySelect.value : "soft";
          if (!foodName) return null;
          return {
            food_name: foodName,
            category,
            severity,
          };
        })
        .filter(Boolean);

      await withError(async () => {
        const requests = [
          api(`/api/users/${userId}/preferences`, "PUT", preferencesPayload),
          api(`/api/users/${userId}/fitness-capabilities`, "POST", fitnessPayload),
          api(`/api/users/${userId}`, "PATCH", {
            ai_provider: form.ai_provider?.value || "anthropic",
            api_key_ref: form.api_key_ref?.value?.trim() || null,
            onboarding_done: true,
          }),
        ];

        foodPreferencePayloads.forEach((pref) => {
          requests.push(api(`/api/users/${userId}/food-preferences`, "POST", pref));
        });

        const results = await Promise.all(requests);
        const [preferencesRes, fitnessRes, userRes, ...foodResponses] = results;
        setOutput("#onboarding-output", {
          message: "Onboarding selesai",
          user: userRes?.data,
          preferences: preferencesRes?.data,
          fitness_capability: fitnessRes?.data,
          food_preferences: foodResponses.map((item) => item?.data).filter(Boolean),
        });
        window.location.href = "/user/home";
      }, "#onboarding-output");

    });
  }

  if (page === "ai_setup") {
    qs("#btn-request-revision")?.addEventListener("click", () => {
      setOutput("#proposal-output", "Catatan revisi tersimpan. AI akan membuat ulang draft program.");
    });

    qs("#btn-edit-manual")?.addEventListener("click", () => {
      setOutput("#proposal-output", "Mode edit manual aktif. Kamu bisa ubah target sebelum apply.");
    });

    qs("#proposal-apply-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const workoutPlanBody = {
          fitness_level_at: 1,
          status: "active",
          goal_type: f.goal_type.value,
          target_weight_kg: toNum(f.target_weight_kg.value),
          weeks_data: { weeks: [] },
          ai_generated: true,
        };
        const mealPlanBody = {
          status: "active",
          target_calories: toNum(f.target_calories.value),
          target_protein_g: toNum(f.target_protein_g.value),
          target_carbs_g: toNum(f.target_carbs_g.value),
          target_fat_g: toNum(f.target_fat_g.value),
          days_data: { days: [] },
          ai_generated: true,
        };
        const [workout, meal] = await Promise.all([
          api(`/api/users/${userId}/workout-plans`, "POST", workoutPlanBody),
          api(`/api/users/${userId}/meal-plans`, "POST", mealPlanBody),
        ]);
        setOutput("#proposal-output", { message: "Program berhasil diaktifkan", workout, meal });
      }, "#proposal-output");
    });
  }

  if (page === "log_meals") {
    qs("#meal-log-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const body = {
          log_date: f.log_date.value,
          meal_type: f.meal_type.value,
          food_name: f.food_name.value.trim(),
          portion_desc: f.portion_size.value || "normal",
          calories: toNum(f.calories.value),
          protein_g: toNum(f.protein_g.value) || 0,
          carbs_g: toNum(f.carbs_g.value) || 0,
          fat_g: toNum(f.fat_g.value) || 0,
          ai_estimated: false,
          is_manual_input: true,
          allergy_flag: false,
        };
        const data = await api(`/api/users/${userId}/meal-logs`, "POST", body);
        setOutput("#meal-output", data);
        const tip = qs("#meal-success-tip");
        if (tip) tip.textContent = `+${body.calories} kcal ditambahkan`;
      }, "#meal-output");
    });

    qs("#meal-log-list-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const fromDate = f.from_date.value;
        const toDate = f.to_date.value;
        const params = new URLSearchParams();
        if (fromDate) params.set("from", fromDate);
        if (toDate) params.set("to", toDate);
        const query = params.toString() ? `?${params.toString()}` : "";
        const data = await api(`/api/users/${userId}/meal-logs${query}`);
        setOutput("#meal-output", data);
      }, "#meal-output");
    });
  }

  if (page === "log_workout") {
    qs("#workout-session-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const body = {
          plan_id: null,
          session_date: f.session_date.value,
          completed: f.completed.checked,
          completion_pct: toNum(f.completion_pct.value) || 0,
          duration_min: toNum(f.duration_min.value),
          exercises_log: f.exercise_name.value.trim()
            ? [{ name: f.exercise_name.value.trim(), sets: 0, reps: 0, weight_kg: 0 }]
            : [],
          user_notes: null,
        };
        const data = await api(`/api/users/${userId}/workout-sessions`, "POST", body);
        setOutput("#workout-output", data);
        const tip = qs("#workout-success-tip");
        if (tip) tip.textContent = "Great work! +35 discipline points (jika sesuai rule hari ini).";
      }, "#workout-output");
    });

    qs("#day-score-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const body = {
          total_score: toNum(f.total_score.value),
          workout_pts: 0,
          nutrition_pts: 0,
          sleep_pts: 0,
          logging_pts: 0,
          bonus_pts: 0,
          penalty_pts: 0,
          workout_done: f.workout_done.checked,
          is_rest_day: false,
          calories_actual: toNum(f.calories_actual.value) || 0,
          calories_target: toNum(f.calories_target.value) || 0,
          sleep_hours_actual: toNum(f.sleep_hours_actual.value) || 0,
          sleep_hours_target: toNum(f.sleep_hours_target.value) || 0,
        };
        const data = await api(`/api/users/${userId}/day-scores/${f.score_date.value}`, "PUT", body);
        setOutput("#workout-output", data);
      }, "#workout-output");
    });
  }

  if (page === "workout_program") {
    qs("#workout-plan-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const body = {
          fitness_level_at: toNum(f.fitness_level_at.value),
          status: f.status.value,
          goal_type: f.goal_type.value,
          target_weight_kg: toNum(f.target_weight_kg.value),
          weeks_data: { weeks: [] },
          ai_generated: f.ai_generated.checked,
        };
        const data = await api(`/api/users/${userId}/workout-plans`, "POST", body);
        setOutput("#workout-plan-output", data);
      }, "#workout-plan-output");
    });

    qs("#workout-plan-list-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const status = f.status.value.trim();
        const query = status ? `?status=${encodeURIComponent(status)}` : "";
        const data = await api(`/api/users/${userId}/workout-plans${query}`);
        setOutput("#workout-plan-output", data);
      }, "#workout-plan-output");
    });

    qs("#btn-activate-workout-plan")?.addEventListener("click", async () => {
      const userId = qs("#activate-workout-user-id")?.value.trim();
      const planId = qs("#activate-workout-plan-id")?.value.trim();
      if (!userId || !planId) return setOutput("#workout-plan-output", "User ID and Plan ID required");
      saveUserId(userId);
      await withError(async () => {
        const data = await api(`/api/users/${userId}/workout-plans/${planId}/activate`, "POST", {});
        setOutput("#workout-plan-output", data);
      }, "#workout-plan-output");
    });
  }

  if (page === "meal_plan") {
    qs("#meal-plan-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const body = {
          status: f.status.value,
          target_calories: toNum(f.target_calories.value),
          target_protein_g: toNum(f.target_protein_g.value),
          target_carbs_g: toNum(f.target_carbs_g.value),
          target_fat_g: toNum(f.target_fat_g.value),
          days_data: { days: [] },
          ai_generated: f.ai_generated.checked,
        };
        const data = await api(`/api/users/${userId}/meal-plans`, "POST", body);
        setOutput("#meal-plan-output", data);
      }, "#meal-plan-output");
    });

    qs("#meal-plan-list-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const status = f.status.value.trim();
        const query = status ? `?status=${encodeURIComponent(status)}` : "";
        const data = await api(`/api/users/${userId}/meal-plans${query}`);
        setOutput("#meal-plan-output", data);
      }, "#meal-plan-output");
    });

    qs("#btn-activate-meal-plan")?.addEventListener("click", async () => {
      const userId = qs("#activate-meal-user-id")?.value.trim();
      const planId = qs("#activate-meal-plan-id")?.value.trim();
      if (!userId || !planId) return setOutput("#meal-plan-output", "User ID and Plan ID required");
      saveUserId(userId);
      await withError(async () => {
        const data = await api(`/api/users/${userId}/meal-plans/${planId}/activate`, "POST", {});
        setOutput("#meal-plan-output", data);
      }, "#meal-plan-output");
    });
  }

  if (page === "progress") {
    qs("#progress-query-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      const params = new URLSearchParams();
      if (f.from_date.value) params.set("from", f.from_date.value);
      if (f.to_date.value) params.set("to", f.to_date.value);
      const query = params.toString() ? `?${params.toString()}` : "";

      await withError(async () => {
        const [activeProgram, weightLogs, dayScores] = await Promise.all([
          api(`/api/users/${userId}/active-program`),
          api(`/api/users/${userId}/weight-logs${query}`),
          api(`/api/users/${userId}/day-scores${query}`),
        ]);
        setOutput("#progress-active-program", activeProgram);
        setOutput("#progress-weight-logs", weightLogs);
        setOutput("#progress-day-scores", dayScores);
      }, "#progress-active-program");
    });
  }

  if (page === "weekly_review") {
    const getUser = () => qs("#review-user-id")?.value.trim();

    qs("#btn-weekly-review")?.addEventListener("click", async () => {
      const userId = getUser();
      if (!userId) return setOutput("#weekly-review-output", "User ID required");
      saveUserId(userId);
      await withError(async () => {
        const data = await api(`/api/users/${userId}/reviews/weekly`);
        setOutput("#weekly-review-output", data);
      }, "#weekly-review-output");
    });

    qs("#btn-monthly-trigger")?.addEventListener("click", async () => {
      const userId = getUser();
      if (!userId) return setOutput("#monthly-review-output", "User ID required");
      saveUserId(userId);
      await withError(async () => {
        const data = await api(`/api/users/${userId}/reviews/monthly/check-trigger`, "POST", {});
        setOutput("#monthly-review-output", data);
      }, "#monthly-review-output");
    });

    qs("#btn-monthly-mark-done")?.addEventListener("click", async () => {
      const userId = getUser();
      if (!userId) return setOutput("#monthly-review-output", "User ID required");
      saveUserId(userId);
      await withError(async () => {
        const data = await api(`/api/users/${userId}/reviews/monthly/mark-done`, "POST", {});
        setOutput("#monthly-review-output", data);
      }, "#monthly-review-output");
    });

    qs("#btn-fitness-history")?.addEventListener("click", async () => {
      const userId = getUser();
      if (!userId) return setOutput("#monthly-review-output", "User ID required");
      saveUserId(userId);
      await withError(async () => {
        const data = await api(`/api/users/${userId}/fitness-capabilities`);
        setOutput("#monthly-review-output", data);
      }, "#monthly-review-output");
    });
  }

  if (page === "settings") {
    qs("#settings-user-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const body = {
          ai_provider: f.ai_provider.value,
          api_key_ref: f.api_key_ref.value.trim() || null,
        };
        const data = await api(`/api/users/${userId}`, "PATCH", body);
        setOutput("#settings-output", data);
      }, "#settings-output");
    });

    qs("#settings-prompt-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const f = event.currentTarget;
      const userId = f.user_id.value.trim();
      saveUserId(userId);
      await withError(async () => {
        const methodName = f.method_name.value.trim();
        const data = await api(`/api/users/${userId}/ai-prompts?method_name=${encodeURIComponent(methodName)}`);
        setOutput("#settings-output", data);
      }, "#settings-output");
    });
  }
});
