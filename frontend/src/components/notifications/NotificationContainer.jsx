import { AnimatePresence } from "framer-motion";
import useNotificationStore from "../../stores/notificationStore";
import Notification from "./Notification";

const NotificationContainer = () => {
	const { notifications, removeNotification } = useNotificationStore();

	return (
		<div className="fixed top-4 right-0 z-[90] w-full px-4 sm:right-4 sm:px-0 sm:w-auto sm:max-w-sm">
			<div className="space-y-4">
				<AnimatePresence>
					{notifications.map((notification) => (
						<Notification key={notification.id} notification={notification} onRemove={removeNotification} />
					))}
				</AnimatePresence>
			</div>
		</div>
	);
};

export default NotificationContainer;
