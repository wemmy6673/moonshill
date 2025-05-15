const STORAGE_PREFIX = "moonshill_";

const safeStringify = (value) => {
	try {
		return JSON.stringify(value);
	} catch (error) {
		console.error("Error stringifying value:", error);
		return "";
	}
};

const safeParse = (value) => {
	try {
		return JSON.parse(value);
	} catch (error) {
		console.error("Error parsing stored value:", error);
		return null;
	}
};

export const getStorage = (key, defaultValue = null) => {
	try {
		const prefixedKey = `${STORAGE_PREFIX}${key}`;
		const value = localStorage.getItem(prefixedKey);
		return value ? safeParse(value) : defaultValue;
	} catch (error) {
		console.error(`Error getting storage key "${key}":`, error);
		return defaultValue;
	}
};

export const setStorage = (key, value) => {
	try {
		const prefixedKey = `${STORAGE_PREFIX}${key}`;
		const stringifiedValue = safeStringify(value);
		if (stringifiedValue === "") {
			return false;
		}
		localStorage.setItem(prefixedKey, stringifiedValue);
		return true;
	} catch (error) {
		console.error(`Error setting storage key "${key}":`, error);
		return false;
	}
};

export const removeStorage = (key) => {
	try {
		const prefixedKey = `${STORAGE_PREFIX}${key}`;
		localStorage.removeItem(prefixedKey);
		return true;
	} catch (error) {
		console.error(`Error removing storage key "${key}":`, error);
		return false;
	}
};

export const clearStorage = () => {
	try {
		const keys = Object.keys(localStorage);
		keys.forEach((key) => {
			if (key.startsWith(STORAGE_PREFIX)) {
				localStorage.removeItem(key);
			}
		});
		return true;
	} catch (error) {
		console.error("Error clearing storage:", error);
		return false;
	}
};

export const hasStorage = (key) => {
	try {
		const prefixedKey = `${STORAGE_PREFIX}${key}`;
		return localStorage.getItem(prefixedKey) !== null;
	} catch (error) {
		console.error(`Error checking storage key "${key}":`, error);
		return false;
	}
};

export const getStorageKeys = () => {
	try {
		const keys = Object.keys(localStorage);
		return keys.filter((key) => key.startsWith(STORAGE_PREFIX)).map((key) => key.slice(STORAGE_PREFIX.length));
	} catch (error) {
		console.error("Error getting storage keys:", error);
		return [];
	}
};

export const getStorageSize = (key) => {
	try {
		const prefixedKey = `${STORAGE_PREFIX}${key}`;
		const value = localStorage.getItem(prefixedKey);
		return value ? new Blob([value]).size : 0;
	} catch (error) {
		console.error(`Error getting storage size for key "${key}":`, error);
		return 0;
	}
};

export const isStorageAvailable = () => {
	try {
		const testKey = `${STORAGE_PREFIX}test`;
		localStorage.setItem(testKey, "test");
		localStorage.removeItem(testKey);
		return true;
	} catch (error) {
		console.error("localStorage is not available:", error);
		return false;
	}
};
