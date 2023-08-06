# vcd Extension Backend

_Extensibility for cloud management tools._

Framework that extends VMWare's vCloud Director APIs.  Relies on and extends [`pyvcloud`](https://github.com/vmware/pyvcloud) SDK.

## Installation

### Install vcd Extension package
To install vcd Extension Backend package execute the following command:

```shell
python -m pip install vcd-extension
```

### Installation in Development Mode
To install in Development Mode, follow these steps.

1. Clone the repository.

   Use one of the following options: SSH key or HTTPs.

Using Git [SSH key](https://gitlab.fing.edu.uy/help/ssh/README#gitlab-and-ssh-keys):

```shell
git clone git@gitlab.fing.edu.uy:proyecto-grado-vcloud/vcd-extension-backend.git
```

Using HTTPS:

```shell
git clone https://gitlab.fing.edu.uy/proyecto-grado-vcloud/vcd-extension-backend.git
```

2. Create and activate the Python Virtual Environment. This is an optional, but highly recommended step.

```shell
cd vcd-extension-backend
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the project in develop mode.

```shell
python setup.py develop
```

4. Start working on it!!!

## Starting the Server

When installed in development mode an example script to start the server is available under directory `usecases`.
So, after installing in development mode, follow these steps:

1. Set `usecases` as working directory.

```shell
cd usecases
```

2. Edit `config.yml` file to reflect the settings of your environment, like server IP, port, credentials, etc.

   See documentation for parameter's reference.


3. Run the shell script to start the server.

```shell
chmod u+x start_server.sh
./start_server.sh
```

## Testing

### Unit Testing

*TO-DO!!!*

### Backend Endpoints Use Cases Testing

See directory tests

## Notes

This project makes part of a final degree course for Computer Engineering in FING - UDELAR.  The project's goal is to
extend vCloud Director by developing a higher-level intermediate API that interacts with the different APIs of
the product, providing a single programmatic entry point to the different capabilities of the software.

## License

Apache 2.0
