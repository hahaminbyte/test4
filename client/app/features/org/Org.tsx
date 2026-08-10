import React, { FormEvent, useState } from 'react';
import { Alert, Button, Form } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { Card, CardContent, CardHeader, Spinner } from '~/components/ui';
import { OrgDetails } from '~/features/org/components/OrgDetails';
import { useOrg } from '~/hooks/useOrg/useOrg';
import { getApiErrorMessage } from '~/utils/getApiErrorMessage';
import { useCreateOrgMutation, useGetOrgsQuery } from '~/store';
import { LoaderFunction } from 'react-router';
import { rootStore as store } from '~/store';
import { haztrakApi } from '~/store/htApi.slice';

export const orgLoader: LoaderFunction = async ({ request }) => {
  const searchTerm = new URL(request.url).searchParams.get('org');
  if (!searchTerm) return null;
  const orgQuery = store.dispatch(haztrakApi.endpoints.getOrg.initiate(searchTerm));

  return orgQuery
    .unwrap()
    .catch((_err) => null)
    .finally(() => orgQuery.unsubscribe());
};

function CreateOrgForm() {
  const [name, setName] = useState('');
  const [createOrg, { isLoading, error }] = useCreateOrgMutation();
  const navigate = useNavigate();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const org = await createOrg({ name }).unwrap();
      navigate(`/organization?org=${org.slug}`, { replace: true });
    } catch {
      // shown below
    }
  };

  return (
    <Form onSubmit={(e) => void onSubmit(e)} className="tw-mx-auto tw-max-w-md">
      <h2 className="h4 mb-3">Create your organization</h2>
      <p className="text-muted">
        New accounts start without organization access. Create one to manage sites and manifests.
      </p>
      {error ? (
        <Alert variant="danger">{getApiErrorMessage(error, 'Could not create organization.')}</Alert>
      ) : null}
      <Form.Group className="mb-3" controlId="orgName">
        <Form.Label>Organization name</Form.Label>
        <Form.Control
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Acme Waste Services"
          required
          minLength={2}
        />
      </Form.Group>
      <Button type="submit" variant="primary" disabled={isLoading || name.trim().length < 2}>
        {isLoading ? 'Creating…' : 'Create organization'}
      </Button>
    </Form>
  );
}

export const Org = () => {
  const { data: orgs, isLoading: orgsLoading } = useGetOrgsQuery();
  const {
    org: { data: org, isLoading },
  } = useOrg();

  if (orgsLoading || isLoading) return <Spinner />;

  if (!orgs || orgs.length === 0) {
    return (
      <div className="tw-flex tw-justify-center tw-p-6">
        <Card className="tw-max-w-screen-md tw-grow">
          <CardContent className="tw-p-6">
            <CreateOrgForm />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!org) return <div className="tw-p-6">Organization not found</div>;

  return (
    <div className="tw-flex tw-justify-center">
      <Card className="tw-max-w-screen-lg tw-grow">
        <CardHeader id="hero" className="tw-block tw-flex-initial">
          <OrgDetails org={org} />
        </CardHeader>
        <CardContent></CardContent>
      </Card>
    </div>
  );
};
