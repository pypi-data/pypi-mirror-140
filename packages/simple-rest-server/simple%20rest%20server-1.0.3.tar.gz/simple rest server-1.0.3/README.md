# simple rest server
An easy and simple way to test api flows. 

### test method example

```python
def test_mock_with_callback(server):
    # Arrange
    payload = "poop"
    url = "/test"
    server.add_callback_response(url, lambda : payload)

    # Act
    response = requests.get(server.base_url + url)

    # Assert
    assert 200 == response.status_code
    assert payload == response.data.decode()

```