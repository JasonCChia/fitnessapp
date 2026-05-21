document.addEventListener("DOMContentLoaded", async () => {
  const page = document.body.dataset.page || "generic";

  const qs = (selector) => document.querySelector(selector);
  const qsa = (selector) => Array.from(document.querySelectorAll(selector));
  const todayISO = () => new Date().toISOString().slice(0, 10);
  const toNum = (value) => (value === "" || value === null || value === undefined ? null : Number(value));

  const setText = (selector, value) => {
    const el = qs(selector);
    if (!el) return;
    el.textContent = String(value ?? "-");
  };

  const setOutput = (selector, data) => {
    const el = qs(selector);
    if (!el) return;
    if (typeof data === "string") {
      el.textContent = data;
      return;
    }
    el.textContent = JSON.stringify(data, null, 2);
  };

  const api = async (url, method = "GET", body = null) => {
    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body !== null) {
      options.body = JSON.stringify(body);
    }
    const response = await fetch(url, options);
    const json = await response.json();
    if (!response.ok) {
      throw new Error(json.message || json.detail || "Request failed");
    }
    return json;
  };

  const withError = async (fn, outputSelector) => {
    try {
      await fn();
    } catch (error) {
      setOutput(outputSelector, { error: error.message });
    }
  };

  let sessionUser = null;
  try {
    const me = await api("/api/auth/me");
    sessionUser = me?.data?.user || null;
  } catch (_error) {
    if (!["/user/login", "/user/register"].includes(window.location.pathname)) {
      window.location.href = "/user/login";
      return;
    }
  }

  const getCurrentUserId = () => {
    if (!sessionUser?.user_id) {
      throw new Error("Session user tidak ditemukan. Silakan login ulang.");
    }
    return sessionUser.user_id;
  };

  // Keep hidden compatibility for old templates containing user_id inputs.
  qsa("input[name='user_id']").forEach((el) => {
    if (sessionUser?.user_id) el.value = sessionUser.user_id;
    el.type = "hidden";
    el.required = false;
  });

  if (page === "dashboard") {
    await withError(async () => {
      const userId = getCurrentUserId();
      const today = todayISO();
      const [prefsRes, activeRes, scoreRes, fitnessRes, weightRes] = await Promise.all([
        api(`/api/users/${userId}/preferences`),
        api(`/api/users/${userId}/active-program`),
        api(`/api/users/${userId}/day-scores?from=${today}&to=${today}`),
        api(`/api/users/${userId}/fitness-capabilities`),
        api(`/api/users/${userId}/weight-logs?to=${today}`),
      ]);

      const prefs = prefsRes?.data || {};
      const mealPlan = activeRes?.data?.meal_plan || {};
      const todayRows = scoreRes?.data || [];
      const todayScore = Array.isArray(todayRows) && todayRows.length > 0 ? todayRows[0] : {};
      const latestFitness = fitnessRes?.data?.latest || {};
      const weights = weightRes?.data || [];
      const latestWeight = Array.isArray(weights) && weights.length > 0 ? weights[0] : {};

      setText("#ctx-user-info", `${sessionUser?.name || "-"} • ${sessionUser?.email || "tanpa email"}`);
      setText("#dash-goal-type", prefs.goal_type || "-");
      setText("#dash-target-sleep", prefs.sleep_target_hours ?? "-");
      setText("#dash-target-calories", mealPlan.target_calories ?? "-");
      setText("#dash-today-score", todayScore.total_score ?? "-");
      setText("#dash-workout-done", todayScore.workout_done ? "Ya" : "Belum");
      setText("#dash-calories-actual", todayScore.calories_actual ?? "-");
      setText("#dash-user-name", sessionUser?.name || "-");
      setText("#dash-fitness-level", latestFitness.fitness_level ?? "-");
      setText("#dash-latest-weight", latestWeight.weight_kg ?? "-");
    }, "#dashboard-output");
  }

  if (page === "onboarding") {
    const panels = qsa(".coach-panel");
    const dots = qsa(".coach-step-dot");
    const backBtn = qs("#onboarding-back");
    const nextBtn = qs("#onboarding-next");
    const submitBtn = qs("#onboarding-submit");
    const stepLabel = qs("#onboarding-step-label");
    let step = 1;

    const calculateAge = (birthDate) => {
      if (!birthDate) return null;
      const dob = new Date(birthDate);
      if (Number.isNaN(dob.getTime())) return null;
      const today = new Date();
      let age = today.getFullYear() - dob.getFullYear();
      const m = today.getMonth() - dob.getMonth();
      if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age -= 1;
      return age >= 0 ? age : null;
    };

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

    if (sessionUser) {
      const age = calculateAge(sessionUser.birth_date);
      setText("#onboarding-profile-name", sessionUser.name || "-");
      setText("#onboarding-profile-email", sessionUser.email || "-");
      setText("#onboarding-profile-age", age !== null ? `Umur: ${age}` : "Umur: -");
      setText("#onboarding-profile-gender", `Gender: ${sessionUser.gender || "-"}`);
      setText("#onboarding-profile-height", `Tinggi: ${sessionUser.height_cm ?? "-"} cm`);
    }

    const foodPrefList = qs("#food-pref-list");
    qs("#btn-add-food-pref")?.addEventListener("click", () => {
      if (!foodPrefList) return;
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
          <button type="button" class="btn btn-outline-danger btn-remove-food-pref">-</button>
        </div>
      `;
      foodPrefList.appendChild(row);
    });

    foodPrefList?.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("btn-remove-food-pref")) return;
      const row = target.closest(".food-pref-row");
      const rows = qsa(".food-pref-row");
      if (!row) return;
      if (rows.length <= 1) {
        const input = row.querySelector("[data-food-name]");
        if (input instanceof HTMLInputElement) input.value = "";
        return;
      }
      row.remove();
    });

    qs("#onboarding-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const form = event.currentTarget;

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

        const foodPrefs = qsa(".food-pref-row")
          .map((row) => {
            const nameInput = row.querySelector("[data-food-name]");
            const catInput = row.querySelector("[data-food-category]");
            const sevInput = row.querySelector("[data-food-severity]");
            const foodName = nameInput instanceof HTMLInputElement ? nameInput.value.trim() : "";
            const category = catInput instanceof HTMLSelectElement ? catInput.value : "disliked";
            const severity = sevInput instanceof HTMLSelectElement ? sevInput.value : "soft";
            if (!foodName) return null;
            return { food_name: foodName, category, severity };
          })
          .filter(Boolean);

        const requests = [
          api(`/api/users/${userId}/preferences`, "PUT", preferencesPayload),
          api(`/api/users/${userId}/fitness-capabilities`, "POST", fitnessPayload),
          api(`/api/users/${userId}`, "PATCH", {
            onboarding_done: true,
          }),
        ];
        foodPrefs.forEach((pref) => requests.push(api(`/api/users/${userId}/food-preferences`, "POST", pref)));

        await Promise.all(requests);
        window.location.href = "/user/ai-setup";
      }, "#onboarding-output");
    });

    renderStep();
  }

  if (page === "ai_setup") {
    const form = qs("#proposal-apply-form");
    const feedbackInput = qs("#ai-revision-feedback");

    const setTargetSummary = (cal, protein, sleep) => {
      setText("#ai-target-calories-label", cal ?? "-");
      setText("#ai-target-protein-label", protein ?? "-");
      setText("#ai-sleep-target-label", sleep ?? "-");
    };

    await withError(async () => {
      const userId = getCurrentUserId();
      const [prefsRes, activeRes] = await Promise.all([
        api(`/api/users/${userId}/preferences`),
        api(`/api/users/${userId}/active-program`),
      ]);
      const prefs = prefsRes?.data || {};
      const activeMeal = activeRes?.data?.meal_plan || null;

      if (!form) return;
      if (prefs.goal_weight_kg !== undefined && prefs.goal_weight_kg !== null) form.target_weight_kg.value = prefs.goal_weight_kg;
      if (prefs.goal_type) form.goal_type.value = prefs.goal_type;

      const calories = activeMeal?.target_calories ?? toNum(form.target_calories.value) ?? 2100;
      const protein = activeMeal?.target_protein_g ?? toNum(form.target_protein_g.value) ?? 145;
      const carbs = activeMeal?.target_carbs_g ?? toNum(form.target_carbs_g.value) ?? 230;
      const fat = activeMeal?.target_fat_g ?? toNum(form.target_fat_g.value) ?? 70;
      form.target_calories.value = calories;
      form.target_protein_g.value = protein;
      form.target_carbs_g.value = carbs;
      form.target_fat_g.value = fat;

      setTargetSummary(calories, protein, prefs.sleep_target_hours || 8);
    }, "#proposal-output");

    qs("#btn-request-revision")?.addEventListener("click", async () => {
      await withError(async () => {
        if (!form) return;
        const data = await api("/api/ai/revise-proposal", "POST", {
          feedback: (feedbackInput?.value || "").trim(),
          target_calories: toNum(form.target_calories.value),
          target_protein_g: toNum(form.target_protein_g.value),
          target_carbs_g: toNum(form.target_carbs_g.value),
          target_fat_g: toNum(form.target_fat_g.value),
        });
        const revised = data?.data?.revised || {};
        if (revised.target_calories) form.target_calories.value = revised.target_calories;
        if (revised.target_protein_g) form.target_protein_g.value = revised.target_protein_g;
        if (revised.target_carbs_g) form.target_carbs_g.value = revised.target_carbs_g;
        if (revised.target_fat_g) form.target_fat_g.value = revised.target_fat_g;
        setTargetSummary(revised.target_calories, revised.target_protein_g, revised.sleep_target_hours);
        if (Array.isArray(revised.workout_preview)) {
          revised.workout_preview.slice(0, 4).forEach((line, idx) => setText(`#ai-preview-day-${idx + 1}`, line));
        }
        setOutput("#proposal-output", data);
      }, "#proposal-output");
    });

    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const workoutPlanBody = {
          fitness_level_at: 1,
          status: "active",
          goal_type: form.goal_type.value,
          target_weight_kg: toNum(form.target_weight_kg.value),
          weeks_data: { weeks: [] },
          ai_generated: true,
        };
        const mealPlanBody = {
          status: "active",
          target_calories: toNum(form.target_calories.value),
          target_protein_g: toNum(form.target_protein_g.value),
          target_carbs_g: toNum(form.target_carbs_g.value),
          target_fat_g: toNum(form.target_fat_g.value),
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
    const mealForm = qs("#meal-log-form");
    const photoForm = qs("#food-photo-form");
    const listForm = qs("#meal-log-list-form");
    if (mealForm && !mealForm.log_date.value) mealForm.log_date.value = todayISO();

    mealForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const f = event.currentTarget;
        const body = {
          log_date: f.log_date.value,
          meal_type: f.meal_type.value,
          food_name: f.food_name.value.trim(),
          portion_desc: "normal",
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
      }, "#meal-output");
    });

    photoForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const fileInput = photoForm.food_image;
        if (!fileInput?.files?.length) throw new Error("Pilih foto makanan dulu");
        const fd = new FormData();
        fd.append("food_image", fileInput.files[0]);
        const response = await fetch("/api/ai/analyze-food-photo", { method: "POST", body: fd });
        const json = await response.json();
        if (!response.ok) throw new Error(json.message || "Gagal analisa foto");
        const data = json?.data || {};
        if (mealForm) {
          mealForm.food_name.value = data.label || mealForm.food_name.value;
          mealForm.calories.value = data.estimated_calories || mealForm.calories.value;
          mealForm.protein_g.value = data.estimated_protein_g || mealForm.protein_g.value;
          mealForm.carbs_g.value = data.estimated_carbs_g || mealForm.carbs_g.value;
          mealForm.fat_g.value = data.estimated_fat_g || mealForm.fat_g.value;
        }
        setOutput("#meal-output", json);
      }, "#meal-output");
    });

    listForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const f = event.currentTarget;
        const params = new URLSearchParams();
        if (f.from_date.value) params.set("from", f.from_date.value);
        if (f.to_date.value) params.set("to", f.to_date.value);
        const query = params.toString() ? `?${params.toString()}` : "";
        const data = await api(`/api/users/${userId}/meal-logs${query}`);
        setOutput("#meal-output", data);
      }, "#meal-output");
    });
  }

  if (page === "log_workout") {
    const workoutForm = qs("#workout-session-form");
    const scoreForm = qs("#day-score-form");
    const today = todayISO();
    if (workoutForm && !workoutForm.session_date.value) workoutForm.session_date.value = today;
    if (scoreForm && !scoreForm.score_date.value) scoreForm.score_date.value = today;

    await withError(async () => {
      const userId = getCurrentUserId();
      const [prefsRes, activeRes] = await Promise.all([
        api(`/api/users/${userId}/preferences`),
        api(`/api/users/${userId}/active-program`),
      ]);
      const prefs = prefsRes?.data || {};
      const mealPlan = activeRes?.data?.meal_plan || {};
      if (scoreForm) {
        if (prefs.sleep_target_hours !== undefined && prefs.sleep_target_hours !== null) {
          scoreForm.sleep_hours_target.value = prefs.sleep_target_hours;
        }
        if (mealPlan.target_calories) {
          scoreForm.calories_target.value = mealPlan.target_calories;
        }
      }
    }, "#workout-output");

    workoutForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const f = event.currentTarget;
        const body = {
          plan_id: null,
          session_date: f.session_date.value,
          completed: f.completed.checked,
          completion_pct: f.completed.checked ? 100 : 0,
          duration_min: toNum(f.duration_min.value),
          exercises_log: [],
          user_notes: null,
        };
        const data = await api(`/api/users/${userId}/workout-sessions`, "POST", body);
        setOutput("#workout-output", data);
      }, "#workout-output");
    });

    scoreForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const f = event.currentTarget;
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

  if (page === "progress") {
    qs("#progress-query-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const f = event.currentTarget;
        const params = new URLSearchParams();
        if (f.from_date.value) params.set("from", f.from_date.value);
        if (f.to_date.value) params.set("to", f.to_date.value);
        const query = params.toString() ? `?${params.toString()}` : "";
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
    qs("#btn-weekly-review")?.addEventListener("click", async () => {
      await withError(async () => {
        const userId = getCurrentUserId();
        const data = await api(`/api/users/${userId}/reviews/weekly`);
        setOutput("#weekly-review-output", data);
      }, "#weekly-review-output");
    });

    qs("#btn-monthly-trigger")?.addEventListener("click", async () => {
      await withError(async () => {
        const userId = getCurrentUserId();
        const data = await api(`/api/users/${userId}/reviews/monthly/check-trigger`, "POST", {});
        setOutput("#monthly-review-output", data);
      }, "#monthly-review-output");
    });

    qs("#btn-monthly-mark-done")?.addEventListener("click", async () => {
      await withError(async () => {
        const userId = getCurrentUserId();
        const data = await api(`/api/users/${userId}/reviews/monthly/mark-done`, "POST", {});
        setOutput("#monthly-review-output", data);
      }, "#monthly-review-output");
    });

    qs("#btn-fitness-history")?.addEventListener("click", async () => {
      await withError(async () => {
        const userId = getCurrentUserId();
        const data = await api(`/api/users/${userId}/fitness-capabilities`);
        setOutput("#monthly-review-output", data);
      }, "#monthly-review-output");
    });
  }

  if (page === "settings") {
    qs("#settings-prompt-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await withError(async () => {
        const userId = getCurrentUserId();
        const f = event.currentTarget;
        const methodName = f.method_name.value.trim();
        const data = await api(`/api/users/${userId}/ai-prompts?method_name=${encodeURIComponent(methodName)}`);
        setOutput("#settings-output", data);
      }, "#settings-output");
    });
  }
});
