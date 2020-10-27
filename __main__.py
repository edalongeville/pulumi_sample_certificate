"""
DNS nameservers
"""
import pulumi
from pulumi_aws import route53, Provider, acm

domain = "mydomain.com"

# Create a new zone
zone = route53.Zone(
    resource_name="my-zone",
    name=domain,
)
pulumi.export("domain", domain)
pulumi.export("zone_id", getattr(zone, "id"))
pulumi.export("name_servers", zone.name_servers)

# Provider
provider_us_east = Provider(
    resource_name="aws-provider-us-east-1",
    region="us-east-1",
)

# Certificate
certificate = acm.Certificate(
    resource_name="certificate",
    domain_name=domain,
    subject_alternative_names=[f"*.{domain}"],
    validation_method="DNS",
    opts=pulumi.ResourceOptions(
        provider=provider_us_east,
    ),
)

validation_record = route53.Record(
    resource_name="record-certificate-validation",
    name=certificate.domain_validation_options[0]["resourceRecordName"],
    records=[certificate.domain_validation_options[0]["resourceRecordValue"]],
    ttl=300,
    type=certificate.domain_validation_options[0]["resourceRecordType"],
    zone_id=zone.zone_id,
    opts=pulumi.ResourceOptions(
        # NB: Route53 is a Global Service so it doesn't matter which provider we use
        provider=provider_us_east
    ),
)

pulumi.export("certificate_arn", certificate.arn)
