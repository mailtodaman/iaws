# iAWS Application

In the evolving business landscape, a growing number of enterprises are transitioning to cloud platforms, underlining the importance of proficient management of cloud resources as a key aspect of web operations. AWS, GCP, and Azure offer a comprehensive range of services such as S3, EC2, RDS (AWS), Cloud Storage, Compute Engine (GCP), and Blob Storage, Virtual Machines (Azure) that empower organizations to securely store data, host dynamic websites, and efficiently operate applications. As an organization's infrastructure expands across these platforms, the necessity for tools that facilitate the seamless management of cloud resources becomes paramount.

A viable solution to this challenge is the integration of an HTML table to comprehensively delineate resources across AWS, GCP, and Azure. This approach simplifies data representation and enhances user comprehension, enabling quick assessment of resource status. The format offers functionalities like sorting, filtering, and searching, streamlining the process of identifying issues and implementing solutions.

This interactive HTML table is populated using the AWS SDK, Google Cloud SDK, and Azure SDK, versatile tools that offer a plethora of APIs to access various cloud resources. For example, S3 buckets, Google Cloud Storage buckets, and Azure Blob Storage containers can be showcased within the table by leveraging these SDKs to obtain detailed lists of resources along with pertinent metadata like creation dates and sizes. This method is equally effective for extracting information regarding computing instances across platforms, including their current status, specifications, and initiation dates.

Following the data population within the HTML table, users have the capability to execute multiple simultaneous actions on their resources. This means they can select several resources across AWS, GCP, and Azure, and initiate batch operations such as deletion or halting processes, enhancing efficiency, especially for entities managing resources across multiple cloud platforms.

To further enhance operational efficiency, the application can be configured to export data from the HTML table into a CSV file format. This feature facilitates effortless data sharing among team members or for integration into analytical tools for in-depth analysis. Consequently, this versatility amplifies operational efficacy and productivity, adapting to varied operational contexts.

In summary, integrating an HTML table to delineate resources across AWS, GCP, and Azure can significantly augment the efficiency and productivity of web operations. This user-friendly interface allows for swift issue identification and rectification, and the additional functionalities of batch operations and data exportation to CSV format further bolster efficiency and productivity. With the appropriate tools and strategies at their disposal, web companies of diverse scales can find the management of cloud resources across AWS, GCP, and Azure to be a streamlined and manageable endeavor, ensuring a robust, scalable, and flexible architecture that can adapt to varying business needs and technological advancements.

Deploy and run the AWSSheet Django application using Podman, a daemonless container engine.

## NOTE

You can't sell this product to anyone without our approval.

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
