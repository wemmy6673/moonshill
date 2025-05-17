import { Route, Switch } from "wouter";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Landing from "./pages/Landing";
import NotFound from "./pages/NotFound";
import Campaigns from "./pages/Campaigns";
import CampaignDetails from "./pages/CampaignDetails";
import PlatformCallback from "./pages/PlatformCallback";
import NotificationContainer from "./components/notifications/NotificationContainer";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			refetchOnWindowFocus: false,
			refetchOnMount: false,
			refetchOnReconnect: false,
			retry: false,
			retryDelay: 1000,
		},
		mutations: {
			retry: false,
			retryDelay: 1000,
		},
	},
});

function App() {
	return (
		<QueryClientProvider client={queryClient}>
			<NotificationContainer />
			<Switch>
				<Route path="/login" component={Login} />
				<Route path="/signup" component={Signup} />
				<Route path="/" component={Landing} />
				<Route path="/campaigns" component={Campaigns} />
				<Route path="/campaigns/:id" component={CampaignDetails} />
				<Route path="/platforms/:platform" component={PlatformCallback} />
				<Route path="*" component={NotFound} />
			</Switch>
		</QueryClientProvider>
	);
}

export default App;
