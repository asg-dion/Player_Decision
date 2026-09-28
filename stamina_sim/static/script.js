document.addEventListener("DOMContentLoaded", () => {
	const strategyContainer = document.getElementById("strategy-checkboxes");
	const staminaContainer = document.getElementById("stamina-options");
	const turnsSlider = document.getElementById("turns-slider");
	const turnsValue = document.getElementById("turns-value");
	const repetitionsSlider = document.getElementById("repetitions-slider");
	const repetitionsValue = document.getElementById("repetitions-value");
	const runButton = document.getElementById("run-btn");
	const downloadButton = document.getElementById("download-btn");
	const howItWorksButton = document.getElementById("how-it-works-btn");
	const howItWorksModal = document.getElementById("how-it-works-modal");
	const closeHowItWorksButton = document.getElementById("close-how-it-works");
	const summaryContainer = document.getElementById("summary-table");
	const resultsSubtitle = document.getElementById("results-subtitle");
	const resultsEmptyState = document.getElementById("results-empty-state");
	const scoreChartContainer = document.getElementById("score-chart");
	const successChartContainer = document.getElementById("success-chart");
	const clickSound = document.getElementById("click-sound");
	const backgroundMusic = document.getElementById("bg-music");
	const audioToggle = document.getElementById("audio-toggle");
	let scoreChart = null;
	let successChart = null;

	const playClickSound = () => {
        clickSound.volume = 0.50;
		clickSound.currentTime = 0;
		clickSound.play().catch(() => {});
	};

	const startBackgroundMusic = () => {
		backgroundMusic.volume = 0.15;
		backgroundMusic.play().catch(() => {});
		document.removeEventListener("pointerdown", startBackgroundMusic);
		document.removeEventListener("keydown", startBackgroundMusic);
	};

	const updateAudioToggle = () => {
		const label = backgroundMusic.muted
			? "Unmute background music"
			: "Mute background music";
		audioToggle.textContent = backgroundMusic.muted ? "🔇" : "🔊";
		audioToggle.setAttribute("aria-label", label);
		audioToggle.title = label;
	};

	document.addEventListener("pointerdown", startBackgroundMusic, { once: true });
	document.addEventListener("keydown", startBackgroundMusic, { once: true });
	runButton.addEventListener("click", playClickSound);
	downloadButton.addEventListener("click", playClickSound);
	audioToggle.addEventListener("click", () => {
		backgroundMusic.muted = !backgroundMusic.muted;
		updateAudioToggle();
	});
	updateAudioToggle();

	const strategyWarning = document.createElement("p");
	strategyWarning.className = "inline-warning strategy-warning";
	strategyWarning.setAttribute("role", "alert");
	strategyWarning.textContent = "Select at least one strategy to run.";
	strategyWarning.hidden = true;
	strategyContainer.insertAdjacentElement("afterend", strategyWarning);

	const simulationError = document.createElement("p");
	simulationError.className = "inline-warning simulation-error";
	simulationError.setAttribute("role", "alert");
	simulationError.hidden = true;
	resultsEmptyState.insertAdjacentElement("afterend", simulationError);

	const renderBarChart = (container, existingChart, rows, dataKey, title, color, isRate = false) => {
		existingChart?.destroy();
		const canvas = container.querySelector("canvas");
		canvas.setAttribute("role", "img");
		canvas.setAttribute("aria-label", title);

		return new Chart(canvas.getContext("2d"), {
			type: "bar",
			data: {
				labels: rows.map((row) =>
					row.strategy
						.split("_")
						.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
						.join(" "),
				),
				datasets: [
					{
						label: title,
						data: rows.map((row) => Number(row[dataKey])),
						backgroundColor: color,
						borderRadius: 4,
					},
				],
			},
			options: {
				maintainAspectRatio: false,
				plugins: {
					legend: { display: false },
				},
				scales: {
					x: {
						grid: { color: "#D6E0EA" },
						ticks: { color: "#2C3E50" },
						title: {
							display: true,
							text: "Strategy",
							color: "#2C3E50",
						},
					},
					y: {
						beginAtZero: true,
						grid: { color: "#D6E0EA" },
						ticks: {
							color: "#2C3E50",
							callback: isRate
								? (value) => `${(Number(value) * 100).toFixed(0)}%`
								: undefined,
						},
					},
				},
			},
		});
	};

	fetch("/api/strategies")
		.then((response) => {
			if (!response.ok) {
				throw new Error("Unable to load strategies.");
			}
			return response.json();
		})
		.then((strategies) => {
			strategies.forEach((strategy) => {
				const row = document.createElement("div");
				const checkbox = document.createElement("input");
				const label = document.createElement("label");

				checkbox.type = "checkbox";
				checkbox.id = `strategy-${strategy}`;
				checkbox.name = "strategy";
				checkbox.value = strategy;
				checkbox.checked = true;
				checkbox.addEventListener("click", playClickSound);

				label.htmlFor = checkbox.id;
				label.textContent = strategy
					.split("_")
					.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
					.join(" ");

				row.append(checkbox, label);
				strategyContainer.append(row);
			});
		})
		.catch((error) => {
			console.error(error);
		});

	fetch("/api/stamina-levels")
		.then((response) => {
			if (!response.ok) {
				throw new Error("Unable to load stamina levels.");
			}
			return response.json();
		})
		.then((staminaLevels) => {
			Object.keys(staminaLevels).forEach((level) => {
				const row = document.createElement("div");
				const radio = document.createElement("input");
				const label = document.createElement("label");

				radio.type = "radio";
				radio.id = `stamina-${level}`;
				radio.name = "stamina-level";
				radio.value = level;
				radio.checked = level === "medium";
				radio.addEventListener("click", playClickSound);

				label.htmlFor = radio.id;
				label.textContent = level.charAt(0).toUpperCase() + level.slice(1);

				row.append(radio, label);
				staminaContainer.append(row);
			});
		})
		.catch((error) => {
			console.error(error);
		});

	const updateValue = (slider, output) => {
		output.value = slider.value;
		output.textContent = slider.value;
	};

	const revealResultCard = (container) => {
		container.hidden = false;
		container.classList.remove("is-visible");
		void container.offsetHeight;
		container.classList.add("is-visible");
	};

	const getCurrentSettings = () => ({
		strategies: Array.from(
			strategyContainer.querySelectorAll('input[type="checkbox"]:checked'),
		).map((checkbox) => checkbox.value),
		stamina_level: staminaContainer.querySelector(
			'input[type="radio"]:checked',
		)?.value,
		turns: Number(turnsSlider.value),
		repetitions: Number(repetitionsSlider.value),
	});

	strategyContainer.addEventListener("change", () => {
		if (strategyContainer.querySelector('input[type="checkbox"]:checked')) {
			strategyWarning.hidden = true;
		}
	});

	let previouslyFocusedElement = null;
	const closeHowItWorksModal = () => {
		howItWorksModal.hidden = true;
		previouslyFocusedElement?.focus();
	};

	howItWorksButton.addEventListener("click", playClickSound);
	howItWorksButton.addEventListener("click", () => {
		previouslyFocusedElement = document.activeElement;
		howItWorksModal.hidden = false;
		closeHowItWorksButton.focus();
	});
	closeHowItWorksButton.addEventListener("click", closeHowItWorksModal);
	howItWorksModal.addEventListener("click", (event) => {
		if (event.target === howItWorksModal) {
			closeHowItWorksModal();
		}
	});
	document.addEventListener("keydown", (event) => {
		if (event.key === "Escape" && !howItWorksModal.hidden) {
			closeHowItWorksModal();
		}
	});

	turnsSlider.addEventListener("input", () => {
		updateValue(turnsSlider, turnsValue);
	});
	repetitionsSlider.addEventListener("input", () => {
		updateValue(repetitionsSlider, repetitionsValue);
	});

	updateValue(turnsSlider, turnsValue);
	updateValue(repetitionsSlider, repetitionsValue);

	runButton.addEventListener("click", async () => {
		const settings = getCurrentSettings();
		if (settings.strategies.length === 0) {
			strategyWarning.hidden = false;
			return;
		}

		strategyWarning.hidden = true;
		simulationError.hidden = true;
		const originalButtonText = runButton.textContent;
		runButton.disabled = true;
		runButton.textContent = "Running...";

		try {
			const response = await fetch("/api/run", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(settings),
			});
			const result = await response.json();
			if (!response.ok) {
				throw new Error(result.error || "Simulation request failed.");
			}

			const table = document.createElement("table");
			table.className = "summary-data-table";
			const headers = [
				"Strategy",
				"Avg Score",
				"Avg Success Rate",
				"Avg Stamina Used",
				"Avg Stamina Remaining",
			];
			const thead = document.createElement("thead");
			const headerRow = document.createElement("tr");
			headers.forEach((header) => {
				const cell = document.createElement("th");
				cell.scope = "col";
				cell.textContent = header;
				headerRow.append(cell);
			});
			thead.append(headerRow);
			table.append(thead);

			const tbody = document.createElement("tbody");
			result.summary.forEach((row) => {
				const tableRow = document.createElement("tr");
				const values = [
					row.strategy
						.split("_")
						.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
						.join(" "),
					Number(row.final_score).toFixed(2),
					`${(Number(row.success_rate) * 100).toFixed(2)}%`,
					Number(row.stamina_used).toFixed(2),
					Number(row.stamina_remaining).toFixed(2),
				];
				values.forEach((value, index) => {
					const cell = document.createElement("td");
					cell.textContent = value;
					if (index === 1 && Number(row.stamina_used) === 0) {
						const note = document.createElement("span");
						note.className = "no-actions-note";
						note.textContent = " (no actions taken)";
						cell.append(note);
					}
					tableRow.append(cell);
				});
				tbody.append(tableRow);
			});
			table.append(tbody);
			summaryContainer.replaceChildren(table);
			revealResultCard(summaryContainer);
			resultsEmptyState.hidden = true;
			resultsSubtitle.textContent = `Based on ${settings.repetitions} runs per strategy at ${settings.stamina_level} stamina, ${settings.turns} turns each`;

			revealResultCard(scoreChartContainer);
			scoreChart = renderBarChart(
				scoreChartContainer,
				scoreChart,
				result.summary,
				"final_score",
				"Average Score by Strategy",
				"#35858E",
			);
			revealResultCard(successChartContainer);
			successChart = renderBarChart(
				successChartContainer,
				successChart,
				result.summary,
				"success_rate",
				"Average Success Rate by Strategy",
				"#7CA88C",
				true,
			);
		} catch (error) {
			simulationError.textContent = "Something went wrong running the simulation. Try again.";
			simulationError.hidden = false;
		} finally {
			runButton.disabled = false;
			runButton.textContent = originalButtonText;
		}
	});

	downloadButton.addEventListener("click", async () => {
		const originalButtonText = downloadButton.textContent;
		downloadButton.disabled = true;
		downloadButton.textContent = "Preparing CSV...";

		try {
			const response = await fetch("/api/download", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(getCurrentSettings()),
			});
			if (!response.ok) {
				const errorResult = await response.json();
				throw new Error(errorResult.error || "CSV download failed.");
			}

			const csvBlob = await response.blob();
			const contentDisposition = response.headers.get("Content-Disposition") || "";
			const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
			const filename = filenameMatch?.[1] || "stamina_simulation_results.csv";
			const downloadUrl = URL.createObjectURL(csvBlob);
			const link = document.createElement("a");
			link.href = downloadUrl;
			link.download = filename;
			link.click();
			URL.revokeObjectURL(downloadUrl);
		} catch (error) {
			const message = document.createElement("p");
			message.setAttribute("role", "alert");
			message.textContent = error.message;
			summaryContainer.append(message);
		} finally {
			downloadButton.disabled = false;
			downloadButton.textContent = originalButtonText;
		}
	});
});
