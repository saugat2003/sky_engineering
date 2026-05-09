from __future__ import annotations

import csv
import io
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
from django.apps import apps
from django.core.management import call_command
from django.db import transaction
from django.utils.text import slugify


if not apps.ready:
    django.setup()


from django.contrib.auth import get_user_model

from department.models import Department
from teams.models import (
    AuditTrail,
    ContactChannel,
    Repository,
    Skill,
    SoftwareProduct,
    Team,
    TeamDependency,
    TeamMember,
    TeamType,
)


DEFAULT_PASSWORD = "Password123!"

TEAM_REGISTRY_TSV = """Department	Team Leader	Department Head	Team Name	Jira Project Name	Workstream (MF)	Project (codebase) (Github Repo)	Jira board Link	Development Focus Areas	Key Skills & Technologies	Downstream Dependencies	Dependency Type	Software Owned and Evolved By This Team	Versioning Approaches	Wiki Search Terms	Slack Channels	Daily Standup Time and Link	Agile Practices	Team Wiki	 # of Concurrent Projects
xTV_Web	Olivia Carter	Sebastian Holt	Code Warriors	Client Lightning Xtv	#REF!	tiny.cc/x9b4t	short.ly/a7XbP3	Infrastructure scalability, CI/CD integration, platform resilience	AWS/GCP, Terraform, Kubernetes, CI/CD, Docker, Python, Bash	The Debuggers	Infrastructure Support							fake.ly/X9TQ74M	
xTV_Web	James Bennett	Sebastian Holt	The Debuggers	Client Lightning Xtv	#REF!	bit.ly/3FgTzX	tiny.link/ZpQ4M9	Advanced debugging tools, automated error detection, root cause analysis	Debugging tools (GDB, LLDB), Stack traces, Log analysis, Python, Java	Bit Masters	Bug Resolution							shorter.io/MTX97Q4	
xTV_Web	Emma Richardson	Sebastian Holt	Bit Masters	Client Lightning Xtv	#REF!	t.ly/8YpQm	bitly.io/7XQM94T	Security compliance, encryption techniques, data integrity	Cryptography, Penetration Testing, Security Compliance (ISO 27001)	API Avengers	Security Fixes							tinyjump.me/7T9QX4M	
xTV_Web	Benjamin Hayes	Sebastian Holt	Agile Avengers	Client Lightning Xtv	#REF!	goo.gl/R2X7Pd	shrt.me/M7QXT49	Agile transformation, workflow optimization, lean process improvement	Agile frameworks (Scrum, SAFe, Kanban), Jira, Miro, Confluence	The Sprint Kings	Agile Coaching				peacock-bravo, gst-xtv-commerce, gst-xtv-bravo-frontdoor			noway.cc/QX7MT94	6+
xTV_Web	Sophia Mitchell	Sebastian Holt	Syntax Squad	Client Lightning Xtv	#REF!	tinyurl.com/y7n3lxp2	fakeurl.net/X94TQM7	Automated deployment pipelines, release management, rollback strategies	CI/CD, GitHub Actions, Jenkins, YAML, Kubernetes, Helm Charts	The Feature Crafters	Deployment Pipeline							notreal.co/TQX79M4	
xTV_Web	William Cooper	Sebastian Holt	The Codebreakers	Client Lightning Xtv	#REF!	bit.do/rJ4mT	notreal.ly/MTQX947	Cryptographic security, authentication protocols, secure APIs	Cybersecurity, Ethical Hacking, Encryption (AES, RSA), SSL/TLS	The Encryption Squad	Encryption Logic							zapclick.io/MTQ79X4	
xTV_Web	Isabella Ross	Sebastian Holt	DevOps Dynasty		#REF!	is.gd/Kp4XQ9	quick.li/9X7TQ4M	DevOps best practices, Kubernetes orchestration, cloud automation	Kubernetes, Terraform, Ansible, CI/CD, AWS/GCP, Docker, Linux	Code Warriors	CI/CD Infrastructure							goquick.ly/Q7X9MT4	
xTV_Web	Elijah Parker	Sebastian Holt	Byte Force	Client Lightning Xtv	#REF!	short.io/L2rYQ5	go2.cc/MT7XQ49	Cloud infrastructure, API gateway development, serverless architecture	AWS Lambda, API Gateway, Microservices, GraphQL, Node.js, Go	API Avengers	Cloud Hosting Services							bitnot.cc/X79TQ4M	
xTV_Web	Ava Sullivan	Sebastian Holt	The Cloud Architects	Client Lightning Xtv	#REF!	tiny.cc/mQ7nX8	linktr.ee/7TQX94M	Cloud-native applications, distributed systems, multi-region deployments	Kubernetes, Istio, Terraform, AWS/GCP/Azure, Load Balancing	Byte Force, Cache Me Outside	Service Orchestration							shrinkurl.me/T79XQ4M	
xTV_Web	Noah Campbell	Sebastian Holt	Full Stack Ninjas	Client Lightning Xtv	#REF!	bit.ly/4Yx9TmR	jumpto.me/QX97MT4	Frontend and backend synchronization, API integration, UX/UI consistency	React, Node.js, TypeScript, GraphQL, Next.js, Django, REST APIs	The API Explorers	Frontend Design							tinygo.cc/QXMT749	
xTV_Web	Mia Henderson	Nora Chandler	The Error Handlers	Client Web	#REF!	t.ly/xM7p9Q	tinygo.co/T9X7Q4M	Log aggregation, AI-driven anomaly detection, real-time monitoring	Logging (ELK, Splunk), APM (Datadog, New Relic), Exception Handling	The Debuggers	Error Logging Services							jumplink.io/X7MT9Q4	
xTV_Web	Lucas Foster	Nora Chandler	Stack Overflow Survivors	Client Web	#REF!	goo.gl/YX34Pn	click4.cc/X7TQM94	Knowledge management, engineering playbooks, documentation automation	Technical Documentation, Knowledge Sharing, Confluence, AI Bots	The Scrum Lords	Best Practices Sharing							voidjump.me/MTX97Q4	
xTV_Web	Charlotte Murphy	Nora Chandler	The Binary Beasts	Client Web	#REF!	tinyurl.com/98tXmLp	shortr.io/M9X7QT4	High-performance computing, low-latency data processing, algorithm efficiency	C/C++, Data Structures, Parallel Computing, GPU Programming	The Algorithm Alliance	Data Processing							shortpoint.cc/QX7T9M4	
xTV_Web	Henry Ward	Nora Chandler	API Avengers	Client Web	#REF!	bit.do/ZpL4TQ	fake.li/QXMT749	API security, authentication layers, API scalability	API Security (OAuth, JWT), Postman, OpenAPI/Swagger, REST, gRPC	The Dev Dragons	Secure API Development							clktr.im/T79XQ4M	
xTV_Web	Amelia Brooks	Nora Chandler	The Algorithm Alliance	Client Web	#REF!	is.gd/QxN7T9	notreal.cc/7QX9MT4	Machine learning models, AI-driven analytics, data science applications	Machine Learning, Data Science (Pandas, NumPy, Scikit-learn)	The Codebreakers	Advanced Algorithm Support							redirect4.me/7XMTQ94	
Native TVs	Alexander Perry	Mason Briggs	Data Wranglers	Client Roku TV	#REF!	short.io/7LpX4YQ	trythis.me/TQX79M4	Big data engineering, real-time data streaming, database optimization	SQL, NoSQL, Big Data (Hadoop, Spark, Kafka), Python, ETL	The Bit Manipulators	User Data Insights							quickpath.io/QXMT749	
Native TVs	Evelyn Hughes	Mason Briggs	The Sprint Kings	Client Roku TV	#REF!	tiny.cc/QpM74X	shrtn.co/M7XQT49	Agile backlog management, sprint retrospectives, delivery forecasting	Agile methodologies, Jira, Velocity Metrics, Sprint Planning	The Agile Alchemists	Sprint Planning							short-it.co/TX7QM94	
Native TVs	Daniel Scott	Mason Briggs	Exception Catchers	Client Roku TV	#REF!	bit.ly/X7pL4TQ	smallurl.io/Q7MTX49	Fault tolerance, system resilience, disaster recovery planning	Fault Tolerance, Failover Strategies, Incident Response, SRE	The Debuggers	Critical Fixes							noway.link/X9TQ74M	
Native TVs	Harper Lewis	Mason Briggs	Code Monkeys	Client Roku TV	#REF!	t.ly/M98X7TQ	void.li/MT9X74Q	Patch deployment, rollback automation, version control best practices	Git, Hotfix Management, Patch Deployment, Bash, CI/CD	The Version Controllers	Patch Management							microjump.io/MTX97Q4	
Native TVs	Matthew Reed	Mason Briggs	The Compile Crew	Client Roku TV	#REF!	goo.gl/LpX7TQ9	jumpnow.co/XQT79M4	Compiler optimization, static code analysis, build system improvements	Build Systems (Bazel, CMake, Make), Compiler Optimization	The Bit Manipulators	Code Base Management							tap2go.cc/Q7X9T4M	
Native TVs	Scarlett Edwards	Mason Briggs	Git Good	Client Apple TV	#REF!	tinyurl.com/YXpM749	fakeclick.me/7T9XQ4M	Branching strategies, merge conflict resolution, Git best practices	Git, GitOps, Merge Strategies, Branching Models, GitLab CI/CD	The Version Controllers	Automated Merging							zaptrack.io/MTQ79X4	
Native TVs	Jack Turner	Mason Briggs	The CI/CD Squad	Client Apple TV	#REF!	bit.do/QX74MT9	shortjump.io/TX7Q94M	Continuous integration, automated testing, deployment pipelines	Jenkins, GitHub Actions, GitOps, Terraform, AWS CodePipeline	Syntax Squad	Deployment Rollback Support							notreal.link/X7MT9Q4	
Native TVs	Lily Phillips	Mason Briggs	Bug Exterminators	Client Apple TV	#REF!	is.gd/MX74TQ9	redirect.cc/QX79T4M	Performance profiling, automated test generation, security patching	Test Automation (Selenium, Cypress), Load Testing (JMeter)	The Debuggers	Performance Tuning	Jira, XCode			private channels	09:45:00	Scrum	clickthis.io/T79XQ4M	5 to 6
Native TVs	Samuel Morgan	Mason Briggs	The Agile Alchemists	Client Apple TV	#REF!	short.io/T9Q7MX4	zaplink.io/M7XQT94	Agile maturity assessments, coaching & mentorship, SAFe/LeSS frameworks	Agile Transformation, SAFe, Jira, Value Stream Mapping	Stack Overflow Survivors	Agile Adoption Coaching							fakejump.me/QX7T9M4	
Native TVs	Grace Patterson	Mason Briggs	The Hotfix Heroes	Client Apple TV	#REF!	tiny.cc/X7T9Q4M	noway.to/TQ79MX4	Emergency response, rollback strategies, live system debugging	Real-time Debugging, Rollback Automation, Patch Deployment	The CI/CD Squad, Code Monkeys	Emergency Fixes							shortyfast.cc/T79XQ4M	
Mobile	Owen Barnes	Violet Ramsey	Cache Me Outside	Client Mobile	#REF!	bit.ly/74QMXT9	linkdrop.cc/MTX97Q4	Caching strategies, distributed cache systems, database query optimization	Redis, Memcached, CDN Caching, Cache Invalidation Strategies	The UX Wizards	Distributed Caching Services							shrinkfast.io/QXMT749	
Mobile	Chloe Hall	Violet Ramsey	The Scrum Lords	Client Mobile	#REF!	t.ly/QX7M94T	shrinkto.me/QX7MT49	Agile training, sprint planning automation, process governance	Scrum Mastery, Agile Coaching, Jira, Retrospective Analysis	The Sprint Kings, Agile Avengers	Agile Process Coordination							cliktrack.cc/X7MTQ94	
Mobile	Nathan Fisher	Violet Ramsey	The 404 Not Found	Client Mobile	#REF!	goo.gl/T9XQ74M	quicktap.io/X79TQ4M	Error page personalization, debugging-as-a-service, incident response	Incident Response, HTTP Error Handling, Observability	The Scrum Lords	Repository Management							snapurl.me/TX7QM94	
Mobile	Zoey Stevens	Violet Ramsey	The Version Controllers	Client Mobile	#REF!	tinyurl.com/X74MT9Q	tapgo.co/MX74TQ9	GitOps workflows, repository security, automated versioning	Git, Repository Management, DevSecOps, GitOps	The Compile Crew, The 404 Not Found	Branching Strategy							bitjump.io/MT9X74Q	
Mobile	Caleb Bryant	Violet Ramsey	DevNull Pioneers	Client Mobile	#REF!	bit.do/TQX794M	notareallink.com/Q7X9T4M	Logging frameworks, observability enhancements, error handling APIs	Logging Systems, Observability (Grafana, Prometheus)	The API Explorers	API Documentation							nowayto.cc/Q7X9T4M	
Mobile	Hannah Simmons	Violet Ramsey	The Code Refactors	Client Mobile	Commerce	is.gd/MTX974Q	urlfake.io/MT9X7Q4	Code maintainability, tech debt reduction, automated refactoring tools	Code Cleanup, Tech Debt Management, SonarQube, Refactoring	Bug Exterminators	Legacy Code Cleanup	Jira, confluence, Slack, Microsoft packages			#gst-mobile-commerce-poker-face	10:30:00	Scrum	redirect.me/MTQ79X4	
Mobile	Isaac Jenkins	Violet Ramsey	The Jenkins Juggernauts	Client Mobile	#REF!	short.io/9X74TQM	snapurl.cc/7XMT9Q4	CI/CD pipeline optimization, Jenkins plugin development, infrastructure as code	CI/CD Pipelines, Jenkins Scripting, Kubernetes, YAML	DevOps Dynasty, Git Good	Automated Testing							tapitquick.io/X7MT9Q4	
Mobile	Madison Clarke	Violet Ramsey	Infinite Loopers	Client Mobile	#REF!	tiny.cc/QMTX749	random.ly/XQ79MT4	Frontend performance optimization, UI/UX consistency, component reusability	Frontend Optimization, Performance Metrics, JavaScript, CSS	The Feature Crafters	UI Responsiveness							shorttrack.cc/T79XQ4M	
Mobile	Gabriel Coleman	Violet Ramsey	The Feature Crafters	Client Mobile	#REF!	bit.ly/X7Q9T4M	clickthis.to/MTQ79X4	Feature flagging, A/B testing automation, rapid prototyping	A/B Testing, Feature Flagging, Frontend Frameworks	The Error Handlers, Syntax Squad	Design Feedback							fastzap.me/QX7MT94	
Mobile	Riley Sanders	Violet Ramsey	The Bit Manipulators	Client Mobile	#REF!	t.ly/MTQX794	noreal.co/QX97MT4	Binary data processing, encoding/decoding algorithms, compression techniques	Bitwise Operations, Low-level Optimization, Assembly, C++	The Binary Beasts	ETL Pipelines							noturl.com/TQX79M4	
Mobile	Leo Watson	Violet Ramsey	Kernel Crushers	Client Mobile	#REF!	goo.gl/7QXMT49	fastgo.io/TQ97X4M	Low-level optimization, OS kernel tuning, hardware acceleration	Linux Kernel Development, System Performance, Rust, C	The API Avengers	Low-Level Optimization							voidpath.cc/X9TQ74M	
Mobile	Victoria Price	Adam Sinclair	The Git Masters	Client Mobile	#REF!	tinyurl.com/MTX749Q	shrinkme.co/MXQ79T4	Git automation, monorepo strategies, repository analytics	GitOps, Repository Scaling, Git Automation	The Version Controllers	Best Practices							quickgo.io/MTX97Q4	
Mobile	Julian Bell	Adam Sinclair	The API Explorers		#REF!	bit.do/X7TQ49M	url-shorten.cc/7T9XQ4M	API documentation, API analytics, developer experience optimization	API Testing (Postman, Swagger), API Gateway Management	Full Stack Ninjas	Secure Communication							shrt-now.cc/Q7X9T4M	
Reliability_Tool	Layla Russell	Lucy Vaughn	The Lambda Legends	Client Automation QA	#REF!	is.gd/MTQ974X	tinyway.me/Q7XMT94	Serverless architecture, event-driven development, microservice automation	Serverless Computing, AWS Lambda, Node.js, Python	API Avengers	Serverless Functions							tapclick.io/MTQ79X4	
Reliability_Tool	Ethan Griffin	Lucy Vaughn	The Encryption Squad		#REF!	short.io/T9X47QM	jumpfast.io/TQX79M4	Cybersecurity research, cryptographic key management, secure data storage	Cryptography (AES, RSA, SHA-256), Security Audits	API Avengers, The API Explorers	Cryptographic Security							zippyurl.co/X7MT9Q4	
Reliability_Tool	Aurora Cooper	Lucy Vaughn	The UX Wizards	Client Device as a Service	#REF!	tiny.cc/Q7MTX94	micro.link/X7MT9Q4	Accessibility, user behavior analytics, UI/UX best practices	UI/UX Design, Figma, Adobe XD, Usability Testing	Full Stack Ninjas, Feature Crafters	UI Components							bitshrink.io/T79XQ4M	
Reliability_Tool	Dylan Spencer	Lucy Vaughn	The Hackathon Hustlers	Client SRE	#REF!	bit.ly/MT7XQ49	quickmove.cc/MTX97Q4	Rapid prototyping, proof-of-concept development, hackathon facilitation	Rapid Prototyping, MVP Development, No-Code Tools	The UX Wizards	Rapid Prototyping							jumplink.cc/QX7MT94	
Reliability_Tool	Stella Martinez	Lucy Vaughn	The Frontend Phantoms	Client Apps Tooling	#REF!	t.ly/9T7QX4M	fakejump.io/QX7T9M4	Frontend frameworks, web performance tuning, component libraries	Frontend Frameworks (React, Vue, Angular), Performance Optimization	The API Explorers	UI Enhancements							fakego.me/TQX79M4	
Arch	Levi Bishop	Theodore Knox	The Dev Dragons		#REF!	goo.gl/QXMT974	shorty.cc/T79XQ4M	API integrations, SDK development, plugin architecture	API Development, SDK Development, Plugin Architecture	The Feature Crafters	API Integration							shrinkfast.co/X9TQ74M	
Arch	Eleanor Freeman	Theodore Knox	The Microservice Mavericks	Client CLIP Backend for Frontend	#REF!	tinyurl.com/7T9QMX4	zapit.io/7XMTQ94	Microservice governance, inter-service communication, API gateways	Service Mesh (Istio, Envoy), API Gateway, gRPC	The Code Refactors, Lambda Legends	Service Scaling							tinyurlnow.io/MTX97Q4	
Programme	Hudson Ford	Bella Monroe	The Quantum Coders	Client Support	#REF!	bit.do/X9T7Q4M	bitnotreal.com/QXMT749	Quantum computing simulations, parallel processing, AI-assisted coding	Quantum Computing, Qiskit, Parallel Computing	Kernel Crushers	High-Performance Computing							zapforward.cc/Q7X9T4M	
"""


def clean(value: str | None) -> str:
    value = (value or "").replace("\xa0", " ").strip()
    return "" if value in {"#REF!", "None"} else value


def registry_rows() -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(TEAM_REGISTRY_TSV), delimiter="\t")
    rows = []
    for raw_row in reader:
        row = {clean(key): clean(value) for key, value in raw_row.items()}
        if row.get("Team Name"):
            rows.append(row)
    return rows


def normalize_url(value: str) -> str:
    if not value:
        return ""
    if re.match(r"^[a-z][a-z0-9+.-]*://", value, flags=re.IGNORECASE):
        return value
    return f"https://{value}"


def split_list(value: str) -> list[str]:
    parts = []
    current = []
    depth = 0
    for char in value or "":
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        if char == "," and depth == 0:
            part = clean("".join(current))
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    part = clean("".join(current))
    if part:
        parts.append(part)
    return parts


def username_from_name(full_name: str, existing: set[str]) -> str:
    base = slugify(full_name).replace("-", ".") or "user"
    username = base
    suffix = 2
    while username in existing:
        username = f"{base}.{suffix}"
        suffix += 1
    existing.add(username)
    return username


def email_from_username(username: str) -> str:
    return f"{username}@sky-engineering.local"


def ensure_user(full_name: str, users: dict[str, object], existing_usernames: set[str]):
    User = get_user_model()
    if full_name in users:
        return users[full_name]

    name_parts = full_name.split()
    first_name = name_parts[0] if name_parts else full_name
    last_name = " ".join(name_parts[1:])
    username = username_from_name(full_name, existing_usernames)
    user = User.objects.create_user(
        username=username,
        email=email_from_username(username),
        password=DEFAULT_PASSWORD,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )
    users[full_name] = user
    return user


def primary_slack_channel(value: str) -> str:
    channels = split_list(value)
    if not channels:
        return ""
    first = channels[0]
    if first.lower() == "private channels" or first.startswith("#"):
        return first
    return f"#{first}"


def team_email(team_name: str) -> str:
    return f"{slugify(team_name).replace('-', '.')}@sky-engineering.local"


def dependency_lookup_key(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", name.lower())
    return normalized[3:] if normalized.startswith("the") else normalized


def description_for(row: dict[str, str]) -> str:
    details = [
        f"Team leader: {row['Team Leader']}",
        f"Department head: {row['Department Head']}",
    ]
    if row.get("Dependency Type"):
        details.append(f"Dependency type: {row['Dependency Type']}")
    if row.get("Software Owned and Evolved By This Team"):
        details.append(f"Software owned: {row['Software Owned and Evolved By This Team']}")
    if row.get("# of Concurrent Projects"):
        details.append(f"Concurrent projects: {row['# of Concurrent Projects']}")
    return "\n".join(details)


def seed_database(*, reset: bool = True, migrate: bool = True) -> dict[str, int]:
    if migrate:
        call_command("migrate", interactive=False, verbosity=0)
    if reset:
        call_command("flush", interactive=False, verbosity=0)

    rows = registry_rows()
    existing_usernames: set[str] = set(get_user_model().objects.values_list("username", flat=True))

    with transaction.atomic():
        users = {}
        departments = {}
        teams = {}

        engineering_type = TeamType.objects.create(
            name="Engineering",
            description="Engineering delivery team from Team Registry.xlsx.",
        )

        for row in rows:
            head = ensure_user(row["Department Head"], users, existing_usernames)
            department, _ = Department.objects.update_or_create(
                name=row["Department"],
                defaults={
                    "description": f"{row['Department']} department from Team Registry.xlsx.",
                    "specialisation": row["Jira Project Name"] or row["Development Focus Areas"],
                    "head": head,
                    "is_active": True,
                },
            )
            departments[row["Department"]] = department

        for row in rows:
            leader = ensure_user(row["Team Leader"], users, existing_usernames)
            workstream = row.get("Workstream (MF)")
            team_type = engineering_type
            if workstream:
                team_type, _ = TeamType.objects.get_or_create(
                    name=workstream,
                    defaults={"description": f"{workstream} workstream from Team Registry.xlsx."},
                )

            team = Team.objects.create(
                name=row["Team Name"],
                department=departments[row["Department"]],
                team_type=team_type,
                manager=leader,
                mission=row["Development Focus Areas"],
                description=description_for(row),
                jira_project_name=row["Jira Project Name"] or None,
                jira_board_link=normalize_url(row["Jira board Link"]) or None,
                workstream=workstream or None,
                agile_practices=row["Agile Practices"] or None,
                concurrent_projects=row["# of Concurrent Projects"] or None,
                development_focus=row["Development Focus Areas"] or None,
                key_skills=row["Key Skills & Technologies"] or None,
                versioning_approach=row["Versioning Approaches"] or None,
                email_address=team_email(row["Team Name"]),
                slack_channel=primary_slack_channel(row["Slack Channels"]) or None,
                slack_channels=row["Slack Channels"] or None,
                daily_standup_link=row["Daily Standup Time and Link"] or None,
                team_wiki_url=normalize_url(row["Team Wiki"]) or None,
                wiki_search_terms=row["Wiki Search Terms"] or None,
                status="active",
                is_active=True,
            )
            teams[row["Team Name"]] = team

            TeamMember.objects.create(team=team, user=leader, role=TeamMember.RoleChoices.LEAD, is_active=True)
            ContactChannel.objects.create(
                team=team,
                channel_type="email",
                value=team.email_address,
                is_primary=True,
            )

            slack_channels = split_list(row["Slack Channels"])
            for index, channel in enumerate(slack_channels):
                value = channel if channel.startswith("#") or channel.lower() == "private channels" else f"#{channel}"
                ContactChannel.objects.create(
                    team=team,
                    channel_type="slack",
                    value=value,
                    is_primary=index == 0,
                )

            Repository.objects.create(
                team=team,
                name=f"{row['Team Name']} Repository",
                url=normalize_url(row["Project (codebase) (Github Repo)"]),
                platform="GitHub",
                description=f"Repository link from Team Registry.xlsx for {row['Team Name']}.",
                is_primary=True,
            )

            for product_name in split_list(row["Software Owned and Evolved By This Team"]):
                SoftwareProduct.objects.create(
                    team=team,
                    name=product_name,
                    description=f"Owned and evolved by {row['Team Name']}.",
                )

            skill_objects = []
            for skill_name in split_list(row["Key Skills & Technologies"]):
                skill, _ = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={"description": f"{skill_name} listed in Team Registry.xlsx."},
                )
                skill_objects.append(skill)
            team.skills.set(skill_objects)

            AuditTrail.objects.create(
                team=team,
                edited_by=leader,
                edit_description="Seeded from Team Registry.xlsx.",
            )

        lookup = {dependency_lookup_key(name): team for name, team in teams.items()}
        dependency_count = 0
        skipped_dependencies = []
        for row in rows:
            from_team = teams[row["Team Name"]]
            for dependency_name in split_list(row["Downstream Dependencies"]):
                to_team = teams.get(dependency_name) or lookup.get(dependency_lookup_key(dependency_name))
                if not to_team or to_team == from_team:
                    skipped_dependencies.append(f"{from_team.name} -> {dependency_name}")
                    continue
                _, created = TeamDependency.objects.get_or_create(
                    from_team=from_team,
                    to_team=to_team,
                    defaults={
                        "dependency_type": row["Dependency Type"] or None,
                        "description": (
                            f"{from_team.name} lists {to_team.name} as a downstream dependency "
                            "in Team Registry.xlsx."
                        ),
                    },
                )
                dependency_count += int(created)

    return {
        "users": get_user_model().objects.count(),
        "departments": Department.objects.count(),
        "teams": Team.objects.count(),
        "team_members": TeamMember.objects.count(),
        "skills": Skill.objects.count(),
        "repositories": Repository.objects.count(),
        "software_products": SoftwareProduct.objects.count(),
        "contact_channels": ContactChannel.objects.count(),
        "dependencies": dependency_count,
        "skipped_dependencies": len(skipped_dependencies),
    }


def main() -> None:
    summary = seed_database(reset=True, migrate=True)
    print("Database reset and seeded from Team Registry.xlsx.")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print(f"Default password for seeded users: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    main()
