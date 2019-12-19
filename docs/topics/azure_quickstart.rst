========================
Quickstart - Azure Cloud
========================

Setting up cloud resources using Idem is easy to do, Start by making sure that
idem and the idem Azure providers are installed:

.. code-block:: bash

    pip install idem

This command will install idem from pypi as well as the azure cloud provider.
With these in place start by making a new directory to place your Idem code
tree:

.. code-block:: bash

    mkdir idem_azure
    cd idem_azure

This is where your automation for Azure will be placed. When using Idem you
create automation formulas, these formulas are stored in files with the extension
`.sls` and can be stored in subdirectories. For purposes of making this tutorial
easy we will just use a single sls file to write our formula.

Lets start by making some variables for idem to use, this data gets reused in the
Azure formula. This is in plain text here but a secure secret store system will be
made available soon. Open a file called azure.sls and add your login data:

.. code-block:: yaml

    # azure.sls

    {% set profile = {
        'client_id': '<YOUR CLIENT ID>',
        'secret': '<YOUR SECRET>',
        'subscription_id': '<YOUR SUBSCRIPTION ID>',
        'tenant': 'YOUR TENANT' }% }

Now that your Azure login data is taken care of, we can focus on defining the
interfaces that we need to build. In this example we will be creating a
resource group, network security group, virtual network, and a virtual machine.
Idem's Azure provider supports many more interfaces on Azure, but this is
a good start to show how Idem can be used to get the ball rolling.

Next add the resource group to the same file:

.. code-block:: yaml

    # azure.sls

    {% set profile = {
        'client_id': '<YOUR CLIENT ID>',
        'secret': '<YOUR SECRET>',
        'subscription_id': '<YOUR SUBSCRIPTION ID>',
        'tenant': 'YOUR TENANT' }% }

    Azure Resouse Group:
      azurerm.resource.group.present:
        - name: idem
        - location: eastus
        - tags:
            contact_name: Ashley Miller
            organiaztion: SuperCo
        - connection_auth: {{ profile }}

This stanza defines a resource group. Every stanza needs an ID, in this example
the ID is `Azure Resource Group`. Then we need to reference the underlying
idempotent function to call. The function reference used here is
`azurerm.resource.group.present`. After the function reference we pass the
configuration for the given function. Every function takes a name option and
then the options specific to the defined operation. In this case we are defining
that this resource group needs to be in the eastus location, has some tags, and
pass the connection authentication data.

Now we can add something more complicated, security! The management of a
security group can be complicated, but Idem makes applying the many components
of a security group easy!

.. code-block:: yaml

    # azure.sls

    {% set profile = {
        'client_id': '<YOUR CLIENT ID>',
        'secret': '<YOUR SECRET>',
        'subscription_id': '<YOUR SUBSCRIPTION ID>',
        'tenant': 'YOUR TENANT' }% }

    Azure Resouse Group:
      azurerm.resource.group.present:
        - name: idem
        - location: eastus
        - tags:
            contact_name: Ashley Miller
            organiaztion: Acme
        - connection_auth: {{ profile }}

    Network Security Group:
        azurerm.network.network_security_group.present:
            - name: nsg1
            - resource_group: idem
            - security_rules:
              - name: nsg1_rule1
                priority: 100
                protocol: tcp
                access: allow
                direction: outbound
                source_address_prefix: virtualnetwork
                destination_address_prefix: internet
                source_port_range: '*'
                destination_port_range: '*'
              - name: nsg1_rule2
                priority: 101
                protocol: tcp
                access: allow
                direction: inbound
                source_address_prefix: internet
                destination_address_prefix: virtualnetwork
                source_port_range: '*'
                destination_port_ranges:
                  - '22'
                  - '443'
            - tags:
                contact_name: Ashley MIller
                organization: Acme
            - connection_auth: {{ profile }}

The model continues, with another stanza, ID, function and arguments. This simple
model gets re-used over and over again. Making the setup easy to learn and use.
Even situations where very complicated datasets are required, like a security
group, the data can be passed through!

Now lets add the virtual network:

.. code-block:: yaml

    # azure.sls

    {% set profile = {
        'client_id': '<YOUR CLIENT ID>',
        'secret': '<YOUR SECRET>',
        'subscription_id': '<YOUR SUBSCRIPTION ID>',
        'tenant': 'YOUR TENANT' }% }

    Azure Resouse Group:
      azurerm.resource.group.present:
        - name: idem
        - location: eastus
        - tags:
            contact_name: Ashley Miller
            organiaztion: Acme
        - connection_auth: {{ profile }}

    Network Security Group:
        azurerm.network.network_security_group.present:
            - name: nsg1
            - resource_group: idem
            - security_rules:
              - name: nsg1_rule1
                priority: 100
                protocol: tcp
                access: allow
                direction: outbound
                source_address_prefix: virtualnetwork
                destination_address_prefix: internet
                source_port_range: '*'
                destination_port_range: '*'
              - name: nsg1_rule2
                priority: 101
                protocol: tcp
                access: allow
                direction: inbound
                source_address_prefix: internet
                destination_address_prefix: virtualnetwork
                source_port_range: '*'
                destination_port_ranges:
                  - '22'
                  - '443'
            - tags:
                contact_name: Ashley MIller
                organization: Acme
            - connection_auth: {{ profile }}

    Virtual Network:
      azurerm.network.virtual_network.present:
        - name: vnet1
        - resource_group: idem
        - address_prefixes:
            - '10.0.0.0/8'
        - subnets:
            - name: default
              address_prefix: '10.0.0.0/8'
              network_security_group:
                id: /subscriptions/{{ profile['subscription_id'] }}/resourceGroups/idem/providers/Microsoft.Network/networkSecurityGroups/nsg1
        - tags:
            contact_name: Elmer Fudd Gantry
            organization: Everest
        - connection_auth: {{ profile }}

Finally, we can add a virtual machine, Idem can add availability sets and much
more complicated systems, but this is a quickstart! So add the last stanza:

.. code-block:: yaml

    # azure.sls

    {% set profile = {
        'client_id': '<YOUR CLIENT ID>',
        'secret': '<YOUR SECRET>',
        'subscription_id': '<YOUR SUBSCRIPTION ID>',
        'tenant': 'YOUR TENANT' }% }

    Azure Resouse Group:
      azurerm.resource.group.present:
        - name: idem
        - location: eastus
        - tags:
            contact_name: Ashley Miller
            organiaztion: Acme
        - connection_auth: {{ profile }}

    Network Security Group:
        azurerm.network.network_security_group.present:
            - name: nsg1
            - resource_group: idem
            - security_rules:
              - name: nsg1_rule1
                priority: 100
                protocol: tcp
                access: allow
                direction: outbound
                source_address_prefix: virtualnetwork
                destination_address_prefix: internet
                source_port_range: '*'
                destination_port_range: '*'
              - name: nsg1_rule2
                priority: 101
                protocol: tcp
                access: allow
                direction: inbound
                source_address_prefix: internet
                destination_address_prefix: virtualnetwork
                source_port_range: '*'
                destination_port_ranges:
                  - '22'
                  - '443'
            - tags:
                contact_name: Ashley Miller
                organization: Acme
            - connection_auth: {{ profile }}

    Virtual Network:
      azurerm.network.virtual_network.present:
        - name: vnet1
        - resource_group: idem
        - address_prefixes:
            - '10.0.0.0/8'
        - subnets:
            - name: default
              address_prefix: '10.0.0.0/8'
              network_security_group:
                id: /subscriptions/{{ profile['subscription_id'] }}/resourceGroups/idem/providers/Microsoft.Network/networkSecurityGroups/nsg1
        - tags:
            contact_name: Ashley Miller
            organization: Acme
        - connection_auth: {{ profile }}

    Virtual Machine:
      azurerm.compute.virtual_machine.present:
        - name: idem-vm01
        - resource_group: idem
        - vm_size: Standard_B1s
        - image: 'Canonical|UbuntuServer|18.04-LTS|latest'
        - virtual_network: vnet1
        - subnet: default
        - allocate_public_ip: True
        - ssh_public_keys:
            - /home/localuser/.ssh/id_rsa.pub
        - tags:
            contact_name: Ashley Miller
            organization: Acme
        - connection_auth: {{ profile }}

Here we see that we can define an image to use, resource group, vm options,
tags, and ssh login credentials. Now that our formula is complete we can
execute it! But not so fast! We can run the formula in test mode first so
we can ensure that it will make the changes we expect:

.. code-block:: bash

    idem --sls azure --test

Now you can get a report on all of the resources you are about to create.
If everything looks go go ahead and run it for real!

.. code-block:: bash

    idem --sls azure


That's it! Idem will now execute against the code defined in `azure.sls`.

The `idem` command here assumes that you are in the code dir. This is not
necessary, the idem command can be run with the `-T` option:

.. code-block:: bash

    idem -T <path to code dir> --sls azure
