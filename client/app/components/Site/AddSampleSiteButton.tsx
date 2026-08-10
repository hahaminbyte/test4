import React from 'react';
import { Alert, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { useCreateSampleSiteMutation, useGetOrgsQuery } from '~/store';
import { getApiErrorMessage } from '~/utils/getApiErrorMessage';

interface AddSampleSiteButtonProps {
  className?: string;
  navigateToSite?: boolean;
}

/** Creates a local demo generator site without RCRAInfo API credentials. */
export function AddSampleSiteButton({
  className,
  navigateToSite = true,
}: AddSampleSiteButtonProps) {
  const { data: orgs } = useGetOrgsQuery();
  const [createSampleSite, { isLoading, error }] = useCreateSampleSiteMutation();
  const navigate = useNavigate();
  const orgSlug = orgs?.[0]?.slug;

  if (!orgSlug) return null;

  const onClick = async () => {
    try {
      const site = await createSampleSite({ orgSlug }).unwrap();
      if (navigateToSite && site.handler?.epaSiteId) {
        navigate(`/site/${site.handler.epaSiteId}`);
      }
    } catch {
      // surfaced below
    }
  };

  return (
    <div className={className}>
      {error ? (
        <Alert variant="danger" className="py-2">
          {getApiErrorMessage(error, 'Could not create sample site.')}
        </Alert>
      ) : null}
      <Button variant="outline-primary" disabled={isLoading} onClick={() => void onClick()}>
        {isLoading ? 'Creating…' : 'Add sample site'}
      </Button>
      <p className="text-muted small mb-0 mt-2">
        Creates a local demo generator site so you can explore manifests without EPA credentials.
      </p>
    </div>
  );
}
