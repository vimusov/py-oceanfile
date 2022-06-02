pkgname=oceanfile
pkgver=0
pkgrel=1
pkgdesc='Simplified and lightweight alternative to Seafile server'
url='https://git.vimusov.space/py-oceanfile'
arch=('any')
license=('GPL')
depends=(
    'python-aiohttp'
    'python-systemd'
    'python-tomli'
)
makedepends=(
    'python-build'
    'python-installer'
    'python-wheel'
)
source=()

pkgver()
{
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

prepare()
{
    cp -r ../$pkgname ../setup.cfg ../pyproject.toml .
}

build()
{
    python -m build --wheel --no-isolation
}

package()
{
    python -m installer --destdir="$pkgdir" dist/*.whl
}
