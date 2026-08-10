import React, { useContext } from 'react';
import { LuExternalLink } from 'react-icons/lu';
import { Link } from 'react-router';
import { Button } from '~/components/ui';
import { NavContext, NavContextProps } from '~/features/layout/NavContext';
import { Route } from '~/features/layout/Sidebar/SidebarRoutes';

interface NavItemProps {
  route: Route;
  targetBlank?: boolean;
}

export function NavItem({ route, targetBlank }: NavItemProps) {
  const { showSidebar, setShowSidebar } = useContext<NavContextProps>(NavContext);

  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
  };

  return (
    <Button asChild variant="link">
      <Link to={route.url} target={targetBlank ? '_blank' : undefined} onClick={toggleSidebar}>
        <route.icon color="#0e7490" size={24} className="tw-me-3" />
        <span className="tw-text-lg tw-text-black">{route.text}</span>
        {route.external && <LuExternalLink className="tw-m-2 tw-text-destructive" />}
      </Link>
    </Button>
  );
}
