import os
import shlex
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from app.models.program import Program
from app.models.category import Category
from app.models.topic import Topic
from app.models.option import Option
from app.models.man_page import ManPage
from app.schemas.program import ProgramCreate, ProgramUpdate
from typing import List, Optional

# ==========================================
# CONSTANTS
# ==========================================
SHELL_OPERATORS = ['|', ';', '&&', '||', '>', '>>', '<']
REDIRECT_OPERATORS = {'>', '>>', '<'}
MAX_PROGRAM_TOKENS = 3

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_program(db: Session, program_id: int) -> Optional[Program]:
    """Lấy thông tin Program và kèm theo danh mục của nó"""
    return db.query(Program)\
             .filter(Program.id == program_id)\
             .options(selectinload(Program.categories))\
             .first()


def get_programs(db: Session, skip: int = 0, limit: int = 100) -> List[Program]:
    """Lấy danh sách Program kèm danh mục"""
    return db.query(Program)\
             .options(selectinload(Program.categories))\
             .order_by(Program.created_at.asc())\
             .offset(skip).limit(limit).all()


def get_program_by_name(db: Session, name: str):
    """Lấy lệnh theo tên, không phân biệt hoa/thường và khoảng trắng đầu/cuối (Để kiểm tra trùng lặp khi tạo mới)"""
    return db.query(Program)\
             .filter(func.lower(func.trim(Program.name)) == name.lower().strip())\
             .options(selectinload(Program.categories))\
             .first()


def get_program_by_slug(db: Session, slug: str):
    """Lấy lệnh theo slug (Để kiểm tra trùng lặp khi tạo mới)"""
    return db.query(Program).filter(Program.slug == slug).options(selectinload(Program.categories)).first()


def get_program_details_by_slug(db: Session, slug: str):
    """
    Lấy chi tiết 1 lệnh dựa vào Slug.
    Lưu ý: Không sắp xếp options tại đây để tránh thay đổi trạng thái ORM trong session.
    Việc sắp xếp sẽ được thực hiện ở tầng API nếu cần.
    """
    return db.query(Program).options(
        selectinload(Program.categories),
        selectinload(Program.option_groups),
        selectinload(Program.options),
        selectinload(Program.examples),
        selectinload(Program.man_pages)
    ).filter(Program.slug == slug).first()


def get_program_details(db: Session, program_id: int):
    """
    [QUAN TRỌNG] Lấy toàn bộ chi tiết của 1 lệnh.
    Dùng `selectinload` để tải sẵn Categories, Options, Groups và Examples.
    Việc này giúp tránh lỗi N+1 Query, tăng tốc độ phản hồi API lên gấp nhiều lần!
    """
    return db.query(Program).options(
        selectinload(Program.categories),
        selectinload(Program.option_groups),
        selectinload(Program.options),
        selectinload(Program.examples)
        # selectinload(Program.man_pages) # Mở ra nếu bạn dùng bảng này
    ).filter(Program.id == program_id).first()


def search_programs(db: Session, query: str):
    """
    Tìm kiếm Full-text bằng TSVECTOR trong PostgreSQL.
    Sử dụng toán tử @@ để match với vector đã được index.
    """
    return db.query(Program).filter(
        Program.fts_program_vector.op('@@')(func.plainto_tsquery('simple', query))
    ).all()


def explain_command(db: Session, full_command: str):
    """
    Thuật toán phân tích cú pháp (Parser) hỗ trợ toán tử shell và cờ is_found.
    """
    if not full_command or not full_command.strip():
        return []

    # Giới hạn độ dài input để tránh xử lý quá tải
    if len(full_command) > 2000:
        return []

    # 1. Tách chuỗi. shlex sẽ gộp chuỗi trong ngoặc kép thành một token
    try:
        tokens = shlex.split(full_command)
    except ValueError:
        tokens = full_command.strip().split()

    # Lọc bỏ token rỗng
    tokens = [t for t in tokens if t != '']
    if not tokens:
        return []

    # 2. Xử lý các toán tử shell
    commands_list = []
    current_command = []

    for token in tokens:
        if token in SHELL_OPERATORS:
            # Lưu lệnh trước đó (nếu có)
            if current_command:
                commands_list.append(current_command)
                current_command = []
            # Lưu bản thân toán tử như một lệnh ĐỘC LẬP để giải thích
            commands_list.append([token])
        else:
            current_command.append(token)

    if current_command:
        commands_list.append(current_command)

    # Giới hạn số segment để tránh DoS nhẹ
    if len(commands_list) > 30:
        commands_list = commands_list[:30]

    # 3. Batch query Programs và Options để tránh N+1
    # Thu thập tất cả candidate prefix (tối đa MAX_PROGRAM_TOKENS token) từ mọi segment
    all_candidates = set()
    for cmd_parts in commands_list:
        if not cmd_parts or cmd_parts[0] in SHELL_OPERATORS:
            continue
        # Xử lý đường dẫn: /usr/bin/ls -> ls
        lookup_tokens = list(cmd_parts)
        if '/' in cmd_parts[0]:
            lookup_tokens[0] = os.path.basename(cmd_parts[0])
        for i in range(1, min(MAX_PROGRAM_TOKENS, len(lookup_tokens)) + 1):
            # Dừng nếu gặp operator trong cụm token
            if any(t in SHELL_OPERATORS for t in lookup_tokens[:i]):
                break
            candidate = ' '.join(lookup_tokens[:i]).lower().strip()
            all_candidates.add(candidate)

    programs_by_name = {}
    options_by_program_id = {}

    if all_candidates:
        all_programs = db.query(Program)\
                         .filter(func.lower(func.trim(Program.name)).in_(list(all_candidates)))\
                         .order_by(Program.id)\
                         .all()
        # Build map với key đã strip để tương thích dữ liệu cũ có khoảng trắng thừa
        programs_by_name = {p.name.lower().strip(): p for p in all_programs}

        program_ids = [p.id for p in all_programs]
        if program_ids:
            all_options = db.query(Option).filter(Option.program_id.in_(program_ids)).all()
            for opt in all_options:
                options_by_program_id.setdefault(opt.program_id, []).append(opt)

    results = []
    previous_segment_was_redirect = False

    # 4. Phân tích từng cụm lệnh
    for cmd_parts in commands_list:
        if not cmd_parts:
            continue

        # Xác định loại segment dựa vào token đầu
        segment_type = "operator" if cmd_parts[0] in SHELL_OPERATORS else "command"
        if previous_segment_was_redirect and segment_type == "command":
            segment_type = "redirect_target"
        previous_segment_was_redirect = cmd_parts[0] in REDIRECT_OPERATORS

        # Tìm program bằng longest prefix match
        program = None
        program_end_index = 0

        if segment_type == "command":
            # Nếu token đầu là đường dẫn, dùng basename để lookup
            lookup_tokens = list(cmd_parts)
            if '/' in cmd_parts[0]:
                lookup_tokens[0] = os.path.basename(cmd_parts[0])

            # Tìm prefix dài nhất có trong DB
            for i in range(min(MAX_PROGRAM_TOKENS, len(lookup_tokens)), 0, -1):
                candidate = ' '.join(lookup_tokens[:i]).lower().strip()
                if candidate in programs_by_name:
                    program = programs_by_name[candidate]
                    program_end_index = i
                    break

            # Nếu không match prefix nào, mặc định lấy token đầu
            if program_end_index == 0:
                program_end_index = 1
        else:
            # Operator / redirect_target: dùng toàn bộ token làm tên
            program_end_index = 1

        program_name = ' '.join(cmd_parts[:program_end_index])
        args = cmd_parts[program_end_index:]

        # Đóng gói thông tin Program kèm cờ is_found
        program_info = {
            "id": program.id if program else None,
            "name": program_name,
            "slug": program.slug if program else None,
            "description": program.description if program else None,
            "is_found": bool(program)
        }

        parsed_options_info = []
        unmatched = []

        # Chỉ phân tích args nếu đây là command
        if segment_type == "command":
            short_opt_map_dash = {}        # "-a" (Unix style)
            short_opt_map_dash_lower = {}
            short_opt_map_nodash = {}      # "a"  (BSD style)
            short_opt_map_nodash_lower = {}
            long_opt_map = {}
            long_opt_map_lower = {}

            if program:
                for opt in options_by_program_id.get(program.id, []):
                    if opt.short_name:
                        name = opt.short_name
                        if name.startswith('-'):
                            short_opt_map_dash[name] = opt
                            short_opt_map_dash_lower[name.lower()] = opt
                        else:
                            short_opt_map_nodash[name] = opt
                            short_opt_map_nodash_lower[name.lower()] = opt
                    if opt.long_name:
                        long_opt_map[opt.long_name] = opt
                        long_opt_map_lower[opt.long_name.lower()] = opt

            def lookup_dash(name):
                """Lookup cho user nhập có dấu - (VD: -a). Strict: chỉ tìm trong map dash."""
                opt = short_opt_map_dash.get(name)
                if opt is None:
                    opt = short_opt_map_dash_lower.get(name.lower())
                return opt

            def lookup_nodash(name):
                """Lookup cho user nhập không dấu - (BSD, VD: a). Strict: chỉ tìm trong map no-dash."""
                opt = short_opt_map_nodash.get(name)
                if opt is None:
                    opt = short_opt_map_nodash_lower.get(name.lower())
                return opt

            def lookup_long(flag):
                """2-step lookup: exact match trước, fallback lowercase sau"""
                opt = long_opt_map.get(flag)
                if opt is None:
                    opt = long_opt_map_lower.get(flag.lower())
                return opt

            end_of_options = False
            i = 0

            while i < len(args):
                arg = args[i]

                if end_of_options:
                    unmatched.append(arg)
                    i += 1
                    continue

                if arg == '--':
                    end_of_options = True
                    i += 1
                    continue

                if arg.startswith('--'):
                    # Long option
                    key = arg.split('=', 1)[0]
                    opt = lookup_long(key)

                    value = None
                    if '=' in arg:
                        value = arg.split('=', 1)[1]
                    elif opt and opt.takes_value and i + 1 < len(args):
                        # Lấy arg tiếp theo làm giá trị (space-separated)
                        value = args[i + 1]
                        i += 1  # Skip next arg

                    parsed_options_info.append({
                        "id": opt.id if opt else None,
                        "original_text": arg,
                        "short_name": opt.short_name if opt else None,
                        "long_name": opt.long_name if opt else None,
                        "description": opt.description if opt else None,
                        "is_found": bool(opt),
                        "value": value
                    })
                    i += 1
                    continue

                if arg.startswith('-') and len(arg) > 1:
                    # Bước 1: Thử match nguyên cụm trước (VD: -123)
                    whole_opt = lookup_dash(arg)
                    if whole_opt:
                        value = None
                        if whole_opt.takes_value and i + 1 < len(args):
                            value = args[i + 1]
                            i += 1
                        parsed_options_info.append({
                            "id": whole_opt.id,
                            "original_text": arg,
                            "short_name": whole_opt.short_name,
                            "long_name": whole_opt.long_name,
                            "description": whole_opt.description,
                            "is_found": True,
                            "value": value
                        })
                        i += 1
                        continue

                    # Bước 2: Tách ký tự (VD: -a, -b, -c)
                    j = 1
                    while j < len(arg):
                        char = arg[j]
                        flag = f"-{char}"
                        opt = lookup_dash(flag)

                        value = None
                        if opt and opt.takes_value:
                            remaining = arg[j+1:]
                            if remaining:
                                # Giá trị dính liền: -p2222
                                value = remaining
                                j = len(arg)  # Dừng tách arg này
                            else:
                                # Giá trị từ arg tiếp theo: -p 2222
                                if i + 1 < len(args):
                                    value = args[i + 1]
                                    i += 1  # Skip next arg
                                j = len(arg)  # Dừng tách arg này

                        parsed_options_info.append({
                            "id": opt.id if opt else None,
                            "original_text": flag,
                            "short_name": opt.short_name if opt else None,
                            "long_name": opt.long_name if opt else None,
                            "description": opt.description if opt else None,
                            "is_found": bool(opt),
                            "value": value
                        })
                        j += 1
                    i += 1
                    continue
                # BSD-style flags (tar zcf, ps aux) - chỉ áp dụng nếu program được đánh dấu BSD
                if (program and program.is_bsd_style
                        and not arg.startswith('-') and '/' not in arg and '.' not in arg):
                    # Bước 1: Thử match nguyên cụm trước (VD: 123, +123)
                    whole_opt = lookup_nodash(arg)
                    if whole_opt:
                        value = None
                        if whole_opt.takes_value and i + 1 < len(args):
                            value = args[i + 1]
                            i += 1
                        parsed_options_info.append({
                            "id": whole_opt.id,
                            "original_text": arg,
                            "short_name": whole_opt.short_name,
                            "long_name": whole_opt.long_name,
                            "description": whole_opt.description,
                            "is_found": True,
                            "value": value
                        })
                        i += 1
                        continue

                    # Bước 2: Tách ký tự (VD: a, u, x)
                    if all(lookup_nodash(c) is not None for c in arg):
                        j = 0
                        while j < len(arg):
                            char = arg[j]
                            opt = lookup_nodash(char)

                            value = None
                            if opt.takes_value:
                                remaining = arg[j+1:]
                                if remaining:
                                    value = remaining
                                    j = len(arg)
                                else:
                                    if i + 1 < len(args):
                                        value = args[i + 1]
                                        i += 1
                                    j = len(arg)

                            parsed_options_info.append({
                                "id": opt.id,
                                "original_text": char,
                                "short_name": opt.short_name,
                                "long_name": opt.long_name,
                                "description": opt.description,
                                "is_found": True,
                                "value": value
                            })
                            j += 1
                    else:
                        unmatched.append(arg)
                    i += 1
                    continue

                # Các chuỗi text, đường dẫn, hoặc chuỗi trong ngoặc kép
                unmatched.append(arg)
                i += 1

        results.append({
            "type": segment_type,
            "program": program_info,
            "matched_options": parsed_options_info,
            "unmatched_args": unmatched
        })

    return results


def get_programs_by_category_slug(db: Session, category_slug: str) -> List[Program]:
    """
    Lấy danh sách các lệnh thuộc về một Danh mục (dựa vào slug).
    BAO GỒM CẢ: Các lệnh nằm trong danh mục con của danh mục đó.
    """
    # 1. Tìm Category gốc dựa vào slug
    category = db.query(Category).filter(Category.slug == category_slug).first()
    if not category:
        return []

    # 2. Lấy ID của category này VÀ các category con trực tiếp của nó
    # (Nếu hệ thống của bạn chỉ gán lệnh vào category con thì nó vẫn quét chuẩn)
    category_ids = [category.id]
    for sub in category.subcategories:
        category_ids.append(sub.id)

    # 3. Query JOIN để lấy các Program có chứa ít nhất 1 category_id nằm trong danh sách trên
    # Dùng distinct() để tránh việc 1 lệnh thuộc cả cha lẫn con bị nhân đôi kết quả
    programs = db.query(Program)\
                 .join(Program.categories)\
                 .filter(Category.id.in_(category_ids))\
                 .distinct()\
                 .all()
                 
    return programs


# ==========================================
# LẤY PROGRAMS THEO TOPIC CÓ PHÂN TRANG
# ==========================================
def get_programs_by_topic_slug(
    db: Session, 
    topic_slug: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[Program]:
    """
    Lấy danh sách câu lệnh thuộc về một Hệ sinh thái (Topic) qua slug.
    - Hỗ trợ phân trang (skip, limit) để tối ưu hiệu năng.
    - Sắp xếp theo thời gian tạo từ cũ đến mới (asc) để giữ đúng thứ tự.
    - Dùng distinct() để tránh trùng lặp bản ghi.
    """
    return db.query(Program)\
             .join(Program.categories)\
             .join(Category.topic)\
             .filter(Topic.slug == topic_slug)\
             .distinct()\
             .order_by(Program.created_at.asc())\
             .offset(skip)\
             .limit(limit)\
             .all()

# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_program(db: Session, program_in: ProgramCreate):
    """Tạo lệnh mới, có xử lý tự động gán Danh mục (Categories)"""
    
    # 1. Tách category_ids ra khỏi dữ liệu chính (vì bảng Program không có cột này)
    program_data = program_in.model_dump(exclude={"category_ids"})
    db_program = Program(**program_data)
    
    # 2. Xử lý gán danh mục nếu người dùng có gửi lên
    if program_in.category_ids:
        categories = db.query(Category).filter(Category.id.in_(program_in.category_ids)).all()
        db_program.categories = categories # SQLAlchemy sẽ tự động lưu vào bảng trung gian program_categories

    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


def update_program(db: Session, program_id: int, program_in: ProgramUpdate):
    """Cập nhật lệnh, có hỗ trợ cập nhật lại danh sách Danh mục"""
    db_program = get_program(db, program_id)
    if not db_program:
        return None

    update_data = program_in.model_dump(exclude_unset=True) # Chỉ lấy những trường được gửi lên
    
    # Xử lý cập nhật danh mục riêng biệt
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        # Tìm các danh mục theo ID và gán đè lên danh sách cũ
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        db_program.categories = categories

    # Cập nhật các trường thông tin chữ (name, description, is_featured)
    for key, value in update_data.items():
        setattr(db_program, key, value)

    db.commit()
    db.refresh(db_program)
    return db_program


def delete_program(db: Session, program_id: int):
    """Xóa lệnh (PostgreSQL sẽ tự động CASCADE xóa luôn các Options, Examples...)"""
    db_program = get_program(db, program_id)
    if db_program:
        db.delete(db_program)
        db.commit()
    return db_program


def add_category_to_program(db: Session, program_id: int, category_id: int) -> Optional[Program]:
    """Nối một Danh mục vào một Câu lệnh (Thêm vào bảng trung gian)"""
    program = get_program(db, program_id=program_id)
    category = db.query(Category).filter(Category.id == category_id).first()
    
    # Kiểm tra nếu cả 2 tồn tại và danh mục chưa được gắn vào lệnh này
    if program and category and category not in program.categories:
        program.categories.append(category) # SQLAlchemy tự động xử lý bảng trung gian!
        db.commit()
        db.refresh(program)
        
    return program


def remove_category_from_program(db: Session, program_id: int, category_id: int) -> Optional[Program]:
    """Gỡ một Danh mục khỏi một Câu lệnh (Xóa khỏi bảng trung gian)"""
    program = get_program(db, program_id=program_id)
    category = db.query(Category).filter(Category.id == category_id).first()
    
    # Kiểm tra nếu cả 2 tồn tại và danh mục ĐANG ĐƯỢC GẮN vào lệnh này
    if program and category and category in program.categories:
        program.categories.remove(category) # SQLAlchemy tự động xóa dòng ở bảng trung gian
        db.commit()
        db.refresh(program)
        
    return program


def update_program_categories(db: Session, program_id: int, category_ids: List[int]) -> Optional[Program]:
    """Cập nhật toàn bộ danh mục của một lệnh chỉ bằng 1 mảng ID"""
    program = get_program(db, program_id=program_id)
    if not program:
        return None
        
    # Lấy toàn bộ các object Category hợp lệ dựa vào mảng category_ids gửi lên
    categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
    
    # [PHÉP MÀU SQLALCHEMY] - Gán thẳng mảng object mới vào relationship.
    # SQLAlchemy sẽ tự động so sánh với mảng cũ để xóa cái thừa và thêm cái thiếu!
    program.categories = categories
    
    db.commit()
    db.refresh(program)
    return program


def bulk_update_program_categories(
    db: Session, 
    program_ids: List[int], 
    category_ids: List[int]
) -> List[Program]:
    """
    Cập nhật hàng loạt. 
    Lấy ra tất cả các Program trong mảng program_ids,
    sau đó gán lại mảng categories của chúng bằng các category_ids mới.
    """
    if not program_ids:
        return []

    # 1. Lấy tất cả các Object Program cần cập nhật
    programs = db.query(Program).filter(Program.id.in_(program_ids)).all()
    
    # 2. Lấy tất cả các Object Category chuẩn bị gán vào
    categories = []
    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        
    # 3. Lặp qua từng lệnh và gán mảng danh mục mới (SQLAlchemy sẽ tự lo việc thêm/xóa ở bảng trung gian)
    for program in programs:
        program.categories = categories
        
    # 4. Lưu toàn bộ thay đổi chỉ với 1 lần commit
    db.commit()
    
    # Tùy chọn: Làm mới (refresh) dữ liệu để trả về cho chắc chắn
    for program in programs:
        db.refresh(program)
        
    return programs