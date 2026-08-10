import { RouteLoading } from '~/components/RouteLoading';
import { Dashboard } from './Dashboard';

export function HydrateFallback() {
  return RouteLoading({});
}

export { Dashboard as Component };
export default Dashboard;
