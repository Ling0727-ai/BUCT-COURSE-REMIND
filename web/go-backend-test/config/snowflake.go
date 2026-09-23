package config

import (
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/bwmarrin/snowflake"
)

type SnowflakeGenerator struct {
	node *snowflake.Node
}

var Snowflake *SnowflakeGenerator

func NewSnowflakeGenerator() (*SnowflakeGenerator, error) {
	// 节点 ID 从 SNOWFLAKE_NODE 读取（0-1023）。
	// 原实现硬编码为 1，而 docker-compose 早已传入该变量，
	// 多实例部署时所有实例会生成重复 ID。
	nodeID := int64(1)
	if v := os.Getenv("SNOWFLAKE_NODE"); v != "" {
		n, err := strconv.ParseInt(v, 10, 64)
		if err != nil || n < 0 || n > 1023 {
			return nil, fmt.Errorf("SNOWFLAKE_NODE 必须是 0-1023 之间的整数，当前值: %q", v)
		}
		nodeID = n
	}

	node, err := snowflake.NewNode(nodeID)
	if err != nil {
		return nil, err
	}
	log.Printf("[snowflake] 使用节点 ID: %d", nodeID)
	return &SnowflakeGenerator{node: node}, nil
}

func (s *SnowflakeGenerator) GenerateID() string {
	return s.node.Generate().String()
}
