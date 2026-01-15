/**
 * Idle FX
 * -------
 * Controls the idle float jitter and timing based on wind intensity.
 */

import { importWithVersion } from "./importHandler.js";

const {
	IDLE_FLOAT_BASE_VMIN,
	IDLE_FLOAT_MAX_VMIN,
	IDLE_FLOAT_EXPONENT,
	IDLE_FLOAT_BASE_SECONDS,
	IDLE_FLOAT_MIN_SECONDS,
	IDLE_FLOAT_SPEED_EXPONENT,
	IDLE_FLOAT_JITTER_RATIO
} = await importWithVersion("./animationSettings.js");

export function createIdleFx() {
	let idleFloatBase = IDLE_FLOAT_BASE_VMIN;
	let idleFloatDuration = IDLE_FLOAT_BASE_SECONDS;
	let idleFloatJitterTimer = null;
	let paused = false;

	const applyIdleFloatJitter = () => {
		if (paused) return;
		const jitter = (Math.random() * 2) - 1;
		const amp = Math.max(0.1, idleFloatBase * (1 + (jitter * IDLE_FLOAT_JITTER_RATIO)));
		document.documentElement.style.setProperty("--idle-float-amp", `${amp.toFixed(2)}vmin`);
		if (idleFloatJitterTimer) {
			clearTimeout(idleFloatJitterTimer);
		}
		idleFloatJitterTimer = setTimeout(applyIdleFloatJitter, idleFloatDuration * 1000);
	};

	const stopJitter = () => {
		if (idleFloatJitterTimer) {
			clearTimeout(idleFloatJitterTimer);
			idleFloatJitterTimer = null;
		}
	};

	const setWindIntensity = (intensity) => {
		idleFloatBase =
			IDLE_FLOAT_BASE_VMIN +
			((IDLE_FLOAT_MAX_VMIN - IDLE_FLOAT_BASE_VMIN) * Math.pow(intensity, IDLE_FLOAT_EXPONENT));
		idleFloatDuration =
			IDLE_FLOAT_BASE_SECONDS -
			((IDLE_FLOAT_BASE_SECONDS - IDLE_FLOAT_MIN_SECONDS) * Math.pow(intensity, IDLE_FLOAT_SPEED_EXPONENT));
		document.documentElement.style.setProperty("--idle-float-duration", `${idleFloatDuration.toFixed(2)}s`);
		applyIdleFloatJitter();
	};

	const setPaused = (nextPaused) => {
		const next = !!nextPaused;
		if (paused === next) return;
		paused = next;
		if (paused) {
			stopJitter();
			return;
		}
		applyIdleFloatJitter();
	};

	return {
		setWindIntensity,
		setPaused
	};
}
