import { Route, Switch } from "wouter";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Landing from "./pages/Landing";
import NotFound from "./pages/NotFound";

function App() {
	return (
		<Switch>
			<Route path="/login" component={Login} />
			<Route path="/signup" component={Signup} />
			<Route path="/" component={Landing} />
			<Route path="*" component={NotFound} />
		</Switch>
	);
}

export default App;
