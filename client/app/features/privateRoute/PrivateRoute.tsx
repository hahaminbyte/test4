import { ReactElement, useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router';
import { Spinner } from '~/components/ui';
import { useGetSessionQuery } from '~/store';

/**
 * Require an authenticated session before rendering child routes.
 */
export function PrivateRoute(): ReactElement {
  const location = useLocation();
  const { data, isLoading, isError, refetch } = useGetSessionQuery();

  useEffect(() => {
    void refetch();
  }, [refetch]);

  if (isLoading) {
    return (
      <div className="tw-flex tw-h-screen tw-items-center tw-justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError || !data?.isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export { PrivateRoute as Component };
export default PrivateRoute;
