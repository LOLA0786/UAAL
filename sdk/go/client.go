package uaal

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

type Client struct {
    BaseURL string
    APIKey  string
    Client  *http.Client
}

func New(baseURL, apiKey string) *Client {
    return &Client{BaseURL: baseURL, APIKey: apiKey, Client: &http.Client{Timeout: 10 * time.Second}}
}

func (c *Client) SendAction(adapter string, agentOutput map[string]interface{}) (map[string]interface{}, error) {
    payload := map[string]interface{}{"adapter": adapter, "agent_output": agentOutput}
    b, _ := json.Marshal(payload)
    req, _ := http.NewRequest("POST", fmt.Sprintf("%s/api/v1/actions", c.BaseURL), bytes.NewReader(b))
    req.Header.Set("Content-Type", "application/json")
    if c.APIKey != "" { req.Header.Set("x-api-key", c.APIKey) }
    resp, err := c.Client.Do(req)
    if err != nil { return nil, err }
    defer resp.Body.Close()
    var out map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&out)
    return out, nil
}
