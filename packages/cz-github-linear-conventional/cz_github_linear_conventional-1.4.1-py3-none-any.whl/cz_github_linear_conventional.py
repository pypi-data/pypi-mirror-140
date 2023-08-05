import os
import re
from typing import Any, Dict, List

from commitizen import defaults, git, config
from commitizen.cz.base import BaseCommitizen, BaseConfig
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.cz.exceptions import CzException

__all__ = ["GithubLinearConventionalCz"]


def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")


class GithubLinearConventionalCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern
    bump_map = defaults.bump_map
    commit_parser = defaults.commit_parser
    changelog_pattern = defaults.bump_pattern

    def __init__(self, config: BaseConfig):
        super().__init__(config)
        self.regex_pattern = None

    # Read the config file and check if required settings are available
    conf = config.read_cfg()

    if "linear_base_url" not in conf.settings:
        print(
            "Please add the key linear_base_url to your .cz.yaml|json|toml config file."
        )
        quit()
    if "github_repo" not in conf.settings:
        print("Please add the key github_repo to your .cz.yaml|json|toml config file.")
        quit()
    linear_base_url = conf.settings["linear_base_url"]
    github_repo = conf.settings["github_repo"]
    if "change_type_map" not in conf.settings:
        change_type_map = {
            "feat": "Feat",
            "fix": "Fix",
            "refactor": "Refactor",
            "perf": "Perf",
        }

    def questions(self) -> List[Dict[str, Any]]:
        questions: List[Dict[str, Any]] = [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "fix",
                        "name": "fix: A bug fix. Correlates with PATCH in SemVer",
                    },
                    {
                        "value": "feat",
                        "name": "feat: A new feature. Correlates with MINOR in SemVer",
                    },
                    {"value": "docs", "name": "docs: Documentation only changes"},
                    {
                        "value": "style",
                        "name": (
                            "style: Changes that do not affect the "
                            "meaning of the code (white-space, formatting,"
                            " missing semi-colons, etc)"
                        ),
                    },
                    {
                        "value": "refactor",
                        "name": (
                            "refactor: A code change that neither fixes "
                            "a bug nor adds a feature"
                        ),
                    },
                    {
                        "value": "perf",
                        "name": "perf: A code change that improves performance",
                    },
                    {
                        "value": "test",
                        "name": (
                            "test: Adding missing or correcting " "existing tests"
                        ),
                    },
                    {
                        "value": "build",
                        "name": (
                            "build: Changes that affect the build system or "
                            "external dependencies (example scopes: pip, docker, npm)"
                        ),
                    },
                    {
                        "value": "ci",
                        "name": (
                            "ci: Changes to our CI configuration files and "
                            "scripts (example scopes: GitLabCI)"
                        ),
                    },
                ],
            },
            {
                "type": "input",
                "name": "scope",
                "default": self.read_prefix_from_branch,
                "message": (f"Linear issue id:"),
                "filter": self.parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
                "message": (
                    "Write a short and imperative summary of the code changes: (lower case and no period)\n"
                ),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Provide additional contextual information about the code changes: (press [enter] to skip)\n"
                ),
                "filter": multiple_line_breaker,
            },
            {
                "type": "confirm",
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "name": "is_breaking_change",
                "default": False,
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes: (press [enter] to skip)\n"
                ),
            },
        ]
        return questions

    def read_prefix_from_branch(self, *args) -> str:
        """
        Obtain the Linear issue id from the current active branch.

        | linear-github branch pattern  | supported |\n
        | user/identifier-title         | Yes |\n
        | user/identifier               | Yes |\n
        | username-identifier-title     | No |\n
        | user-identifier               | No |\n
        | identifier-title              | Yes|\n
        | title-identifier              | No |\n
        | identifier                    | Yes |\n
        | feature/identifier-title      | No |\n
        | feature/identifier            | No |\n
        """

        issue_regex_patterns = ["\w+/\w{3}-\d+", "\w{3}-\d+"]
        for regex_pattern in issue_regex_patterns:
            command = "git branch | grep '*' | sed 's/*//g' | grep -E -o '{}'".format(
                regex_pattern
            )
            with os.popen(command) as proc:
                issue_id = proc.read().strip()
                if issue_id:
                    self.regex_pattern = regex_pattern
                    return issue_id

    def parse_scope(self, text):
        """
        Require and validate the scope to be Linear ids.
        Parse the scope and add Linear prefixes if they were specified in the config.
        """

        issueRE = re.compile(r"{}".format(self.regex_pattern))

        issue = text.strip()
        required_validator(issue, msg="Linear scope is required")

        if not issueRE.fullmatch(issue):
            raise InvalidAnswerError(f"Linear scope of '{issue}' is invalid")

        return issue

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        scope = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        message = f"{prefix}{scope}: {subject}{body}{footer}"

        return message

    def example(self) -> str:
        return (
            "fix: correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        PATTERN = (
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"
            r"(\(\S+\))?!?:(\s.*)"
        )
        return PATTERN

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_info.txt")
        with open(filepath, "r") as f:
            content = f.read()
        return content

    def process_commit(self, commit: str) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            return ""
        return m.group(3).strip()

    def changelog_message_builder_hook(
        self, parsed_message: dict, commit: git.GitCommit
    ) -> dict:
        """add github and linear links to the readme"""
        rev = commit.rev
        m = parsed_message["message"]
        if parsed_message["scope"]:
            parsed_message["scope"] = " ".join(
                [
                    f"[{issue_id}]({self.linear_base_url}/issue/{issue_id})"
                    for issue_id in parsed_message["scope"].split(",")
                ]
            )
        parsed_message[
            "message"
        ] = f"{m} [{rev[:5]}](https://github.com/{self.github_repo}/commit/{commit.rev})"
        return parsed_message


class InvalidAnswerError(CzException):
    ...


discover_this = GithubLinearConventionalCz
