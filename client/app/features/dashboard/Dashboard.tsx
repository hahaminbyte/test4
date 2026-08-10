import React, { ReactElement } from 'react';
import { Alert, Col, Container, Row } from 'react-bootstrap';
import { Link } from 'react-router';
import {
  GeneratorStatusAreaChart,
  ManifestCountBarChart,
  ManifestStatusPieChart,
} from '~/components/Charts';
import { AddSampleSiteButton } from '~/components/Site/AddSampleSiteButton';
import { HtCard } from '~/components/legacyUi';
import { Spinner } from '~/components/ui';
import { useTitle } from '~/hooks';
import { useGetDashboardStatsQuery, useGetOrgsQuery, useGetProfileQuery } from '~/store';

/** Dashboard page for logged-in user*/
export function Dashboard(): ReactElement {
  useTitle(`Haztrak`, false, true);
  const { data: stats, isLoading, isError } = useGetDashboardStatsQuery();
  const { data: orgs } = useGetOrgsQuery();
  const { data: profile } = useGetProfileQuery();

  const hasOrgs = (orgs?.length ?? 0) > 0;
  const hasSites = profile?.sites && Object.keys(profile.sites).length > 0;

  if (isLoading) {
    return (
      <div className="tw-flex tw-min-h-64 tw-items-center tw-justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <Container className="py-2 pt-3">
      {!hasOrgs ? (
        <Alert variant="info" className="mb-3">
          You are not a member of an organization yet.{' '}
          <Link to="/organization">Create an organization</Link> to get started, then add RCRAInfo
          credentials on your <Link to="/profile">Profile</Link>.
        </Alert>
      ) : null}
      {hasOrgs && !hasSites ? (
        <Alert variant="warning" className="mb-3">
          <p className="mb-2">
            No sites are available for your account yet. Add a local sample site to explore the app,
            or sync from RCRAInfo on your <Link to="/profile">Profile</Link>.
          </p>
          <AddSampleSiteButton />
        </Alert>
      ) : null}
      {isError ? (
        <Alert variant="danger" className="mb-3">
          Unable to load dashboard statistics.
        </Alert>
      ) : null}
      {!isError && stats && stats.manifestCount === 0 && hasSites ? (
        <Alert variant="secondary" className="mb-3">
          No manifests yet.{' '}
          <Link to="/manifest/new">Create your first manifest</Link> or sync from RCRAInfo.
        </Alert>
      ) : null}
      <Row xs={1} lg={2}>
        <Col className="my-3">
          <HtCard title="Calculated Status" className="p-2">
            <GeneratorStatusAreaChart data={stats?.generatorStatus ?? []} />
          </HtCard>
        </Col>
        <Col className="my-3">
          <HtCard title="Manifest by Status" className="p-2">
            <ManifestStatusPieChart data={stats?.byStatus ?? []} />
          </HtCard>
        </Col>
      </Row>
      <Row>
        <Col>
          <HtCard title="Manifest count" className="p-2">
            <ManifestCountBarChart data={stats?.byMonth ?? []} />
          </HtCard>
        </Col>
      </Row>
    </Container>
  );
}
