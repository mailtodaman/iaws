# iAWS Application

In the current business landscape, an increasing number of enterprises are transitioning to cloud platforms, making the proficient management of AWS resources a pivotal aspect of web operations. AWS offers a plethora of services such as S3, EC2, and RDS that empower organizations to securely store data, host dynamic websites, and efficiently operate applications. Nonetheless, as an organization's infrastructure expands, it becomes imperative to have a tool that facilitates the seamless management of AWS resources.

A viable solution to this predicament is the integration of an HTML table to delineate AWS resources comprehensively. This approach not only simplifies data representation but also enhances user comprehension, enabling them to gauge the status of their resources promptly. Moreover, this format offers functionalities like sorting, filtering, and searching, which streamline the process of pinpointing issues and implementing rectifications.

This interactive HTML table is populated utilizing the AWS SDK, a versatile tool offering a gamut of APIs to access various AWS resources. For instance, one can showcase S3 buckets within the table by leveraging the SDK to obtain a detailed list of buckets along with pertinent metadata like creation dates and sizes. This method is equally effective for extracting information regarding EC2 instances, including their current status, specifications, and initiation date.

Following the data population within the HTML table, users are endowed with the capability to execute multiple simultaneous actions on their resources. This means they can select several resources and initiate batch operations, such as deletion or halting processes, enhancing efficiency, especially for entities managing a considerable number of resources.

Enhancing the operational efficiency further, the application can be configured to export the data from the HTML table into a CSV file format. This feature facilitates effortless data sharing amongst team members or for integration into analytical tools for in-depth analysis. Consequently, this versatility amplifies the operational efficacy and productivity, adapting to varied operational contexts.

In summary, the integration of an HTML table to delineate AWS resources can remarkably augment the efficiency and productivity of web operations. This user-friendly interface allows for swift issue identification and rectification, and the additional functionalities of batch operations and data exportation to CSV format further bolster efficiency and productivity. Hence, with the appropriate tools and strategies at their disposal, web companies of diverse scales can find the management of AWS resources to be a streamlined and manageable endeavor.

Deploy and run the AWSSheet Django application using Podman, a daemonless container engine.

## NOTE

You can't sell this product to anyone without approval from IADS LTD (UK)

## Prerequisites

- Podman installed on your system (check with `podman --version`)
- For macOS and Windows users, Podman machine support is required

## Setup and Deployment

### Podman Machine

For macOS and Windows:

```bash
podman machine init  # Initialize a new Podman machine
podman machine start # Start the machine
podman build -t awssheet .  # Build the container image
podman run --name awssheet --publish 8000:8000 -d awssheet  # Run the container

Access the application at http://localhost:8000.
