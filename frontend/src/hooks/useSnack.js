import useNotificationStore from "../stores/notificationStore";

const useSnack = () => {
	const store = useNotificationStore();

	return {
		success: (message, options) => store.success(message, options),
		error: (message, options) => store.error(message, options),
		warning: (message, options) => store.warning(message, options),
		info: (message, options) => store.info(message, options),
		remove: (id) => store.removeNotification(id),
	};
};

export default useSnack;
