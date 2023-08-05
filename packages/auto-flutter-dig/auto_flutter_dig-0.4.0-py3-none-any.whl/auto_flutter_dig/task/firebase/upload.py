from pathlib import Path, PurePosixPath

from ...core.config import Config
from ...core.os import OS
from ...core.utils import _Dict, _If
from ...model.argument.option import LongOptionWithValue
from ...task.base.process import *
from ...task.firebase._const import (
    FIREBASE_CONFIG_KEY_PATH,
    FIREBASE_DISABLE_INTERACTIVE_MODE,
    FIREBASE_ENV,
)
from ...task.firebase.check import FirebaseCheck
from ...task.firebase.validate import FirebaseBuildValidate
from ...task.flutter.build.stub import FlutterBuildStub
from ...task.identity import FirebaseTaskIdentity


class FirebaseBuildUpload(BaseProcessTask):
    __options = {
        "notes": LongOptionWithValue("notes", "Release notes to include"),
        "testers": LongOptionWithValue(
            "testers", "A comma separated list of tester emails to distribute to"
        ),
        "groups": LongOptionWithValue(
            "groups", "A comma separated list of group aliases to distribute to"
        ),
    }
    identity = FirebaseTaskIdentity(
        "firebase",
        "Upload build to firebase",
        _Dict.flatten(__options),
        lambda: FirebaseBuildUpload(),
    )

    def require(self) -> List[TaskId]:
        return [
            FirebaseBuildValidate.identity.id,
            FirebaseCheck.identity.id,
            FlutterBuildStub.identity.id,
        ]

    def _create_process(self, args: Args) -> ProcessOrResult:
        filename = args.global_get("output")
        if filename is None or len(filename) <= 0:
            return TaskResult(
                args, AssertionError("Previous task does not have output")
            )

        file: Path = Path(OS.posix_to_machine_path(PurePosixPath(filename)))
        if not file.exists():
            return TaskResult(
                args, FileNotFoundError("Output not found: {}".format(str(file)))
            )

        file = file.absolute()
        google_id = args.get(FirebaseBuildValidate.ARG_FIREBASE_GOOGLE_ID)
        if google_id is None or len(google_id) <= 0:
            return TaskResult(args, AssertionError("Google app id not found"))

        arguments: List[str] = [
            FIREBASE_DISABLE_INTERACTIVE_MODE.value,
            "appdistribution:distribute",
            str(file),
            "--app",
            google_id,
        ]

        _If.not_none(
            args.get(self.__options["notes"]),
            lambda notes: arguments.extend(("--release-notes", notes)),
            lambda: None,
        )

        _If.not_none(
            args.get(self.__options["testers"]),
            lambda testers: arguments.extend(("--testers", testers)),
            lambda: None,
        )

        _If.not_none(
            args.get(self.__options["groups"]),
            lambda groups: arguments.extend(("--groups", groups)),
            lambda: None,
        )

        return Process.create(
            Config.get_path(FIREBASE_CONFIG_KEY_PATH),
            arguments=arguments,
            environment=FIREBASE_ENV.value,
            writer=self._print,
        )
