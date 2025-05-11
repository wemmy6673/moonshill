import { create } from "zustand";

const useNotificationStore = create((set) => ({
	notifications: [],
	addNotification: (notification) => {
		const id = Date.now();
		set((state) => ({
			notifications: [...state.notifications, { ...notification, id }],
		}));
		return id;
	},
	removeNotification: (id) => {
		set((state) => ({
			notifications: state.notifications.filter((notification) => notification.id !== id),
		}));
	},
	success: (message, options = {}) => {
		const id = useNotificationStore.getState().addNotification({
			type: "success",
			message,
			duration: options.duration || 5000,
			...options,
		});
		return id;
	},
	error: (message, options = {}) => {
		const id = useNotificationStore.getState().addNotification({
			type: "error",
			message,
			duration: options.duration || 5000,
			...options,
		});
		return id;
	},
	warning: (message, options = {}) => {
		const id = useNotificationStore.getState().addNotification({
			type: "warning",
			message,
			duration: options.duration || 5000,
			...options,
		});
		return id;
	},
	info: (message, options = {}) => {
		const id = useNotificationStore.getState().addNotification({
			type: "info",
			message,
			duration: options.duration || 5000,
			...options,
		});
		return id;
	},
}));

export default useNotificationStore;
