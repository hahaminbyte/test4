import { RouteLoading } from '~/components/RouteLoading';
import { Root, rootLoader } from './Root';

export function HydrateFallback() {
  return RouteLoading({ fullScreen: true });
}

export { rootLoader as loader };
export { Root as Component };
export default Root;
