macord
==========
A simple Discord API wrapper for Python.

Installing
----------
**Python 3.10 or higher is required**

run the following command to install:

    # Linux/macOS
    python3 -m pip install -U macord

    # Windows
    py -3 -m pip install -U macord


Example
--------------

.. code:: py

    import macord

    bot = macord.Bot("TOKEN")

    def on_message_create(bot: macord.Bot, msg: macord.Message):
        if msg.content == 'ping':
            bot.send_message(msg.channel_id, "hello world")
    bot.on_message_create(on_message_create)

    bot.run()
