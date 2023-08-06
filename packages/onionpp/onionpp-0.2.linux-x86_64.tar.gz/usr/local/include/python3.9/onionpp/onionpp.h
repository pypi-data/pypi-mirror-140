//
// Created by nbdy on 14.02.22.
//

#ifndef ONIONPP__ONIONPP_H_
#define ONIONPP__ONIONPP_H_

#include <cstring>
#include <thread>
#include <iostream>

extern "C" {
#include "tor/src/feature/api/tor_api.h"
}

namespace onionpp {
class Tor {
  std::thread m_Thread;

 public:
  Tor(): m_Thread([] { start(); }) {}
  explicit Tor(uint32_t i_u32SocksPort): m_Thread([i_u32SocksPort] { start(i_u32SocksPort); }) {}

  ~Tor() {
    if(m_Thread.joinable()) {
      m_Thread.join();
    }
  }

  static std::string getVersion() {
    return tor_api_get_provider_version();
  }

  static tor_main_configuration_t* createConfiguration(uint32_t i_u32SocksPort) {
    char firstArg[] = "tor";

    char SocksPort[] = "__SocksPort";
    char socksPortValue[6];
    sprintf(socksPortValue, "%d", i_u32SocksPort);

    char* args[] = {
        firstArg,
        SocksPort, socksPortValue
    };

    auto *cfg = tor_main_configuration_new();
    if(tor_main_configuration_set_command_line(cfg, 3, &args[0]) == -1) {
      std::cout << "Could not set cli config arguments." << std::endl;
      tor_main_configuration_free(cfg);
      return nullptr;
    }

    return cfg;
  }

  static bool start(uint32_t i_u32SocksPort = 4269) {
    auto rVal = false;
    auto* cfg = createConfiguration(i_u32SocksPort);
    if(cfg != nullptr) {
      rVal = tor_run_main(cfg) == 0;
      tor_main_configuration_free(cfg);
    }
    return rVal;
  }
};
}

#endif//ONIONPP__ONIONPP_H_
