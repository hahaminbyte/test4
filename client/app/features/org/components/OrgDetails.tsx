import React from 'react';
import { Alert } from 'react-bootstrap';
import { FaCheckCircle } from 'react-icons/fa';
import { FaCircleXmark } from 'react-icons/fa6';
import { Link } from 'react-router';
import { CopyButton } from '~/components/CopyButton/CopyButton';
import { AddSampleSiteButton } from '~/components/Site/AddSampleSiteButton';
import { Organization } from '~/store';

interface OrgDetailsProps {
  org: Organization;
}

export const OrgDetails = ({ org }: OrgDetailsProps) => {
  return (
    <div id="hero" className="tw-block tw-flex-initial">
      <h2 className="tw-text-lg tw-font-bold">{org.name}</h2>
      <div className="tw-mx-4">
        <CopyButton copyText={org.slug} className="tw-self-start tw-ps-0">
          <span>{org.slug}</span>
        </CopyButton>
        <p>
          <span>Is integrated with RCRAInfo: </span>
          {org.rcrainfoIntegrated ? (
            <FaCheckCircle className="text-success tw-inline" />
          ) : (
            <FaCircleXmark className="text-danger tw-inline" />
          )}
        </p>
        {!org.rcrainfoIntegrated ? (
          <Alert variant="info" className="mt-3 mb-0">
            <p className="mb-2">
              RCRAInfo is not connected yet. Open your <Link to="/profile">Profile</Link>, edit the{' '}
              <strong>RCRAInfo Profile</strong> section, enter your preprod API credentials, save,
              then Sync — or add a local sample site to explore without EPA credentials.
            </p>
            <AddSampleSiteButton navigateToSite />
          </Alert>
        ) : (
          <Alert variant="success" className="mt-3 mb-0">
            RCRAInfo credentials are configured. Use <Link to="/site">My Sites</Link> or sync
            manifests from the site/manifest pages.
          </Alert>
        )}
      </div>
    </div>
  );
};
