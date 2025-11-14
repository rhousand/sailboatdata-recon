{
  description = "Sailboat data comparison CLI tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          requests
          beautifulsoup4
          click
          rich
          lxml
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.python311Packages.pip
          ];

          shellHook = ''
            echo "Sailboat Data Comparison Tool - Development Environment"
            echo "Python version: $(python --version)"
            echo ""
            echo "Available commands:"
            echo "  python sailboat_compare.py <boat1> <boat2> [boat3...]"
            echo ""
          '';
        };

        packages.default = pkgs.python311Packages.buildPythonApplication {
          pname = "sailboat-compare";
          version = "0.1.0";
          src = ./.;

          propagatedBuildInputs = with pkgs.python311Packages; [
            requests
            beautifulsoup4
            click
            rich
            lxml
          ];

          meta = with pkgs.lib; {
            description = "CLI tool for comparing sailboat specifications from sailboatdata.com";
            license = licenses.mit;
          };
        };
      }
    );
}
