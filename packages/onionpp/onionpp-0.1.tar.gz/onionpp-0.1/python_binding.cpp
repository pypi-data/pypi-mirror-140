//
// Created by nbdy on 26.02.22.
//

#include "onionpp.h"

#include <pybind11/pybind11.h>

PYBIND11_MODULE(onionpp, m) {
  pybind11::class_<onionpp::Tor> tor(m, "Tor");
  tor.def(pybind11::init([] {
       return new onionpp::Tor;
     }));
  tor.def(pybind11::init([](uint32_t i_u32SocksPort) {
       return new onionpp::Tor(i_u32SocksPort);
     }));

  tor.def("start", &onionpp::Tor::start);
  tor.def("get_version", &onionpp::Tor::getVersion);
}