import React from 'react';
import { Spinner } from '~/components/ui';

export function RouteLoading({ fullScreen = false }: { fullScreen?: boolean }) {
  return (
    <div
      className={
        fullScreen
          ? 'tw-flex tw-h-screen tw-items-center tw-justify-center'
          : 'tw-flex tw-min-h-64 tw-items-center tw-justify-center'
      }
    >
      <Spinner size="lg" />
    </div>
  );
}
