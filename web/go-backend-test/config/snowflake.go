package config

import (
	"github.com/bwmarrin/snowflake"
)

type SnowflakeGenerator struct {
	node *snowflake.Node
}

var Snowflake *SnowflakeGenerator

func NewSnowflakeGenerator() (*SnowflakeGenerator, error) {
	// 创建一个新的 Snowflake 节点，节点ID为1
	node, err := snowflake.NewNode(1)
	if err != nil {
		return nil, err
	}
	return &SnowflakeGenerator{node: node}, nil
}

func (s *SnowflakeGenerator) GenerateID() string {
	return s.node.Generate().String()
}
