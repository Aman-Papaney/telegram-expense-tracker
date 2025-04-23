from setuptools import setup, find_packages

setup(
    name='telegram-expense-tracker',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A Telegram bot for tracking expenses',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/telegram-expense-tracker',
    packages=find_packages(include=['bot', 'bot.*']),
    install_requires=[
        'python-telegram-bot>=13.0',
        'psycopg2-binary',
        'matplotlib',  # optional for visualization
        'plotly'      # optional for visualization
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)