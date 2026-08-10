import { Container } from 'react-bootstrap';
import { Link } from 'react-router';
import { AddSampleSiteButton } from '~/components/Site/AddSampleSiteButton';
import { SiteListGroup } from '~/components/Site';
import { HtCard } from '~/components/legacyUi';
import { Spinner } from '~/components/ui';
import { useTitle } from '~/hooks';
import { useGetOrgsQuery, useGetUserHaztrakSitesQuery } from '~/store';

/** Returns a table displaying the Haztrak sites a user has access to.*/
export function SiteList() {
  useTitle('Sites');
  const { data, isLoading } = useGetUserHaztrakSitesQuery();
  const { data: orgs } = useGetOrgsQuery();
  const hasOrg = (orgs?.length ?? 0) > 0;

  if (isLoading) return <Spinner size="sm" />;

  return (
    <Container className="my-3">
      <HtCard title="My Sites">
        <HtCard.Body>
          {data && data.length > 0 ? (
            <SiteListGroup sites={data} />
          ) : (
            <div className="text-muted text-center">
              <p>No sites to display</p>
              <p>
                Sync RCRAInfo permissions from your <Link to="/profile">Profile</Link>
                {hasOrg ? ', or add a local sample site below.' : '.'}
              </p>
              {hasOrg ? <AddSampleSiteButton className="tw-mx-auto tw-mt-3 tw-max-w-md" /> : null}
            </div>
          )}
        </HtCard.Body>
      </HtCard>
    </Container>
  );
}
