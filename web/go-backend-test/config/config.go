package config

import (
	"os"
)

type Config struct {
	Port  string
	Env   string
	Debug bool
}

var AppConfig *Config

func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = ":8080"
	}

	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}

	debug := env == "development"

	AppConfig = &Config{
		Port:  port,
		Env:   env,
		Debug: debug,
	}

	return AppConfig
}
