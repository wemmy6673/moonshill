import { AnimatePresence } from "framer-motion";
import useNotificationStore from "../../stores/notificationStore";
import Notification from "./Notification";

const NotificationContainer = () => {
	const { notifications, removeNotification } = useNotificationStore();

	return (
		<div className="fixed top-4 right-4 z-50 w-full max-w-sm space-y-4">
			<AnimatePresence>
				{notifications.map((notification) => (
					<Notification key={notification.id} notification={notification} onRemove={removeNotification} />
				))}
			</AnimatePresence>
		</div>
	);
};

export default NotificationContainer;
